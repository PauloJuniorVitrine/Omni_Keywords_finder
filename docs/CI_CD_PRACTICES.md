# Práticas de CI/CD

Este documento detalha as práticas de CI/CD do Omni Keywords Finder.

## GitHub Actions

### 1. CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10]
        node-version: [16.x, 18.x]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Set up Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Install Node.js dependencies
      run: |
        npm ci

    - name: Run Python tests
      run: |
        pytest tests/ --cov=src --cov-report=xml

    - name: Run Node.js tests
      run: |
        npm test -- --coverage

    - name: Upload Python coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

    - name: Upload Node.js coverage
      uses: codecov/codecov-action@v3
      with:
        directory: ./coverage
        fail_ci_if_error: true

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18.x'

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Install Node.js dependencies
      run: |
        npm ci

    - name: Run Python linters
      run: |
        flake8 src tests
        black --check src tests
        isort --check-only src tests
        mypy src tests

    - name: Run Node.js linters
      run: |
        npm run lint
        npm run type-check

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18.x'

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Install Node.js dependencies
      run: |
        npm ci

    - name: Run Python security checks
      run: |
        bandit -r src
        safety check

    - name: Run Node.js security checks
      run: |
        npm audit
        npm run security-check
```

### 2. CD Pipeline

```yaml
# .github/workflows/cd.yml
name: CD

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}

    - name: Build and push API image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./docker/api/Dockerfile
        push: true
        tags: |
          omni-keywords/api:latest
          omni-keywords/api:${{ github.ref_name }}

    - name: Build and push ML image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./docker/ml/Dockerfile
        push: true
        tags: |
          omni-keywords/ml:latest
          omni-keywords/ml:${{ github.ref_name }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: '1.0.0'

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Terraform Init
      run: |
        cd terraform
        terraform init

    - name: Terraform Plan
      run: |
        cd terraform
        terraform plan -var="image_tag=${{ github.ref_name }}"

    - name: Terraform Apply
      run: |
        cd terraform
        terraform apply -auto-approve -var="image_tag=${{ github.ref_name }}"

  notify:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
    - name: Notify Slack
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        fields: repo,message,commit,author,action,eventName,ref,workflow,job,took
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      if: always()
```

## Docker

### 1. API Dockerfile

```dockerfile
# docker/api/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY config/ config/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. ML Dockerfile

```dockerfile
# docker/ml/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY config/ config/
COPY models/ models/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8001

CMD ["uvicorn", "src.ml.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 3. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: docker/api/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongodb
      - redis

  ml:
    build:
      context: .
      dockerfile: docker/ml/Dockerfile
    ports:
      - "8001:8001"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongodb
      - redis

  mongodb:
    image: mongo:5.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  redis:
    image: redis:6.2
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  mongodb_data:
  redis_data:
```

## Observações

- Seguir padrões
- Manter documentação
- Testar adequadamente
- Otimizar performance
- Garantir segurança
- Monitorar sistema
- Revisar código
- Manter histórico
- Documentar decisões
- Revisar periodicamente 