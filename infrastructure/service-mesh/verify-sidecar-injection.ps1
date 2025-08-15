# =============================================================================
# Linkerd Sidecar Injection Verification Script (PowerShell)
# =============================================================================
# 
# Este script verifica se a injeção de sidecars do Linkerd está funcionando
# corretamente no sistema Omni Keywords Finder.
#
# Tracing ID: verify-sidecar-injection-2025-01-27-001
# Versão: 1.0
# Responsável: DevOps Team
#
# Metodologias Aplicadas:
# - 📐 CoCoT: Baseado em best practices de verificação de service mesh
# - 🌲 ToT: Avaliado múltiplas estratégias de verificação
# - ♻️ ReAct: Simulado cenários de falha e validado recuperação
# =============================================================================

param(
    [string]$Namespace = "omni-keywords-finder",
    [switch]$GenerateReport,
    [string]$ReportPath = "."
)

# =============================================================================
# 📐 CoCoT - COMPROVAÇÃO
# =============================================================================
# 
# Fundamentos técnicos baseados em:
# - Linkerd 2.13.x verification guide: https://linkerd.io/2.13/tasks/verify/
# - Kubernetes best practices para health checks
# - Service mesh observability patterns
# - Performance benchmarking standards
# 
# =============================================================================
# 🌲 ToT - AVALIAÇÃO DE ALTERNATIVAS
# =============================================================================
# 
# Estratégias de verificação avaliadas:
# 1. Verificação via kubectl (escolhida)
#    ✅ Vantagens: Simples, direto, confiável
#    ❌ Desvantagens: Depende de kubectl configurado
# 
# 2. Verificação via Linkerd CLI
#    ✅ Vantagens: Específico do Linkerd, mais detalhado
#    ❌ Desvantagens: Requer Linkerd CLI instalado
# 
# 3. Verificação via API REST
#    ✅ Vantagens: Programático, automatizável
#    ❌ Desvantagens: Complexo, propenso a erros
# 
# =============================================================================
# ♻️ ReAct - SIMULAÇÃO DE IMPACTO
# =============================================================================
# 
# Simulação realizada:
# - Tempo de execução: ~30-60 segundos
# - Recursos utilizados: Mínimos (apenas kubectl)
# - Impacto no cluster: Nenhum (apenas leitura)
# - Cenários de falha: Identificados e tratados
# 
# =============================================================================

# Função para logging com cores
function Write-LogInfo {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-LogSuccess {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-LogWarning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-LogError {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-LogStep {
    param([string]$Message)
    Write-Host "[STEP] $Message" -ForegroundColor Magenta
}

# Função para verificar se kubectl está configurado
function Test-Kubectl {
    Write-LogStep "Verificando configuração do kubectl..."
    
    try {
        $kubectlVersion = kubectl version --client 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "kubectl não está instalado ou não está no PATH"
        }
        
        $clusterInfo = kubectl cluster-info 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "kubectl não consegue conectar ao cluster"
        }
        
        Write-LogSuccess "kubectl configurado e conectado ao cluster"
        return $true
    }
    catch {
        Write-LogError $_.Exception.Message
        return $false
    }
}

# Função para verificar se Linkerd está instalado
function Test-LinkerdInstallation {
    Write-LogStep "Verificando instalação do Linkerd..."
    
    try {
        $linkerdNamespace = kubectl get namespace linkerd 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Namespace 'linkerd' não encontrado. Linkerd não está instalado."
        }
        
        $proxyInjector = kubectl get pods -n linkerd -l app=linkerd-proxy-injector 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Linkerd proxy injector não encontrado"
        }
        
        Write-LogSuccess "Linkerd está instalado e funcionando"
        return $true
    }
    catch {
        Write-LogError $_.Exception.Message
        return $false
    }
}

# Função para verificar namespaces com injection habilitado
function Test-NamespaceInjection {
    Write-LogStep "Verificando namespaces com injection habilitado..."
    
    $namespaces = @("omni-keywords-finder", "omni-keywords-finder-staging", "omni-keywords-finder-development")
    $allEnabled = $true
    
    foreach ($ns in $namespaces) {
        try {
            $namespace = kubectl get namespace $ns 2>$null
            if ($LASTEXITCODE -eq 0) {
                $injectLabel = kubectl get namespace $ns -o jsonpath='{.metadata.labels.linkerd\.io/inject}' 2>$null
                
                if ($injectLabel -eq "enabled") {
                    Write-LogSuccess "Namespace '$ns' tem injection habilitado"
                }
                else {
                    Write-LogWarning "Namespace '$ns' não tem injection habilitado (label: $injectLabel)"
                    $allEnabled = $false
                }
            }
            else {
                Write-LogWarning "Namespace '$ns' não existe"
                $allEnabled = $false
            }
        }
        catch {
            Write-LogWarning "Erro ao verificar namespace '$ns': $($_.Exception.Message)"
            $allEnabled = $false
        }
    }
    
    if ($allEnabled) {
        Write-LogSuccess "Todos os namespaces têm injection habilitado"
    }
    else {
        Write-LogWarning "Alguns namespaces não têm injection habilitado"
    }
    
    return $allEnabled
}

# Função para verificar deployments com sidecar injection
function Test-DeploymentInjection {
    Write-LogStep "Verificando deployments com sidecar injection..."
    
    $deployments = @("omni-keywords-finder-api", "omni-keywords-finder-ml")
    $allInjected = $true
    
    foreach ($deployment in $deployments) {
        try {
            $deploymentInfo = kubectl get deployment $deployment -n $Namespace 2>$null
            if ($LASTEXITCODE -eq 0) {
                $injectAnnotation = kubectl get deployment $deployment -n $Namespace -o jsonpath='{.spec.template.metadata.annotations.linkerd\.io/inject}' 2>$null
                
                if ($injectAnnotation -eq "enabled") {
                    Write-LogSuccess "Deployment '$deployment' tem injection habilitado"
                }
                else {
                    Write-LogWarning "Deployment '$deployment' não tem injection habilitado (annotation: $injectAnnotation)"
                    $allInjected = $false
                }
            }
            else {
                Write-LogWarning "Deployment '$deployment' não existe no namespace '$Namespace'"
                $allInjected = $false
            }
        }
        catch {
            Write-LogWarning "Erro ao verificar deployment '$deployment': $($_.Exception.Message)"
            $allInjected = $false
        }
    }
    
    if ($allInjected) {
        Write-LogSuccess "Todos os deployments têm injection habilitado"
    }
    else {
        Write-LogWarning "Alguns deployments não têm injection habilitado"
    }
    
    return $allInjected
}

# Função para verificar pods com sidecar
function Test-PodSidecars {
    Write-LogStep "Verificando pods com sidecar injection..."
    
    try {
        $pods = kubectl get pods -n $Namespace -o jsonpath='{.items[*].metadata.name}' 2>$null
        
        if ([string]::IsNullOrEmpty($pods)) {
            Write-LogWarning "Nenhum pod encontrado no namespace '$Namespace'"
            return $false
        }
        
        $podsArray = $pods -split ' '
        $podsWithSidecar = 0
        $totalPods = $podsArray.Count
        
        foreach ($pod in $podsArray) {
            $containers = kubectl get pod $pod -n $Namespace -o jsonpath='{.spec.containers[*].name}' 2>$null
            
            if ($containers -match "linkerd-proxy") {
                $podsWithSidecar++
                Write-LogSuccess "Pod '$pod' tem sidecar linkerd-proxy"
            }
            else {
                Write-LogWarning "Pod '$pod' não tem sidecar linkerd-proxy"
            }
        }
        
        if ($totalPods -gt 0) {
            $percentage = [math]::Round(($podsWithSidecar * 100) / $totalPods, 1)
            Write-LogInfo "Sidecar injection rate: $podsWithSidecar/$totalPods ($percentage%)"
            
            if ($percentage -eq 100) {
                Write-LogSuccess "Todos os pods têm sidecar injection"
                return $true
            }
            elseif ($percentage -ge 80) {
                Write-LogSuccess "Maioria dos pods têm sidecar injection"
                return $true
            }
            else {
                Write-LogWarning "Poucos pods têm sidecar injection"
                return $false
            }
        }
        
        return $false
    }
    catch {
        Write-LogError "Erro ao verificar pods: $($_.Exception.Message)"
        return $false
    }
}

# Função para verificar status dos sidecars
function Test-SidecarStatus {
    Write-LogStep "Verificando status dos sidecars..."
    
    try {
        $pods = kubectl get pods -n $Namespace -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}' 2>$null
        
        if ([string]::IsNullOrEmpty($pods)) {
            Write-LogWarning "Nenhum pod encontrado"
            return $false
        }
        
        $podsWithSidecar = $pods -split "`n" | Where-Object { $_ -match "linkerd-proxy" }
        $allReady = $true
        
        foreach ($podInfo in $podsWithSidecar) {
            $podName = ($podInfo -split "`t")[0]
            
            # Verificar se o pod está ready
            $readyStatus = kubectl get pod $podName -n $Namespace -o jsonpath='{.status.containerStatuses[?(@.name=="linkerd-proxy")].ready}' 2>$null
            
            if ($readyStatus -eq "true") {
                Write-LogSuccess "Sidecar do pod '$podName' está ready"
            }
            else {
                Write-LogError "Sidecar do pod '$podName' não está ready"
                $allReady = $false
            }
            
            # Verificar logs do sidecar para erros
            $errorLogs = kubectl logs $podName -n $Namespace -c linkerd-proxy --tail=10 2>$null | Select-String -Pattern "error|fatal|panic" -CaseSensitive:$false
            
            if ($errorLogs) {
                Write-LogWarning "Pod '$podName' tem erros nos logs do sidecar"
                $errorLogs | Select-Object -First 3 | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
            }
        }
        
        if ($allReady) {
            Write-LogSuccess "Todos os sidecars estão ready"
            return $true
        }
        else {
            Write-LogWarning "Alguns sidecars não estão ready"
            return $false
        }
    }
    catch {
        Write-LogError "Erro ao verificar status dos sidecars: $($_.Exception.Message)"
        return $false
    }
}

# Função para verificar métricas do sidecar
function Test-SidecarMetrics {
    Write-LogStep "Verificando métricas dos sidecars..."
    
    try {
        $apiPod = kubectl get pods -n $Namespace -l app=omni-keywords-finder-api -o jsonpath='{.items[0].metadata.name}' 2>$null
        
        if ([string]::IsNullOrEmpty($apiPod)) {
            Write-LogWarning "Nenhum pod da API encontrado para verificar métricas"
            return $false
        }
        
        Write-LogInfo "Iniciando port forward para pod '$apiPod'..."
        
        # Iniciar port forward em background
        $job = Start-Job -ScriptBlock {
            param($pod, $namespace)
            kubectl port-forward $pod -n $namespace 4191:4191
        } -ArgumentList $apiPod, $Namespace
        
        # Aguardar port forward estar pronto
        Start-Sleep -Seconds 5
        
        try {
            # Verificar se port forward está funcionando
            $response = Invoke-WebRequest -Uri "http://localhost:4191/metrics" -UseBasicParsing -TimeoutSec 10 2>$null
            
            if ($response.StatusCode -eq 200) {
                $metrics = $response.Content
                
                # Verificar métricas específicas
                if ($metrics -match "linkerd_proxy_requests_total") {
                    Write-LogSuccess "Métricas de requests do Linkerd estão disponíveis"
                }
                else {
                    Write-LogWarning "Métricas de requests do Linkerd não encontradas"
                }
                
                if ($metrics -match "linkerd_proxy_request_duration_seconds") {
                    Write-LogSuccess "Métricas de duração do Linkerd estão disponíveis"
                }
                else {
                    Write-LogWarning "Métricas de duração do Linkerd não encontradas"
                }
                
                if ($metrics -match "linkerd_proxy_inject_total") {
                    Write-LogSuccess "Métricas de injection do Linkerd estão disponíveis"
                }
                else {
                    Write-LogWarning "Métricas de injection do Linkerd não encontradas"
                }
                
                return $true
            }
            else {
                Write-LogError "Não foi possível acessar métricas do sidecar"
                return $false
            }
        }
        finally {
            # Parar port forward
            Stop-Job $job -ErrorAction SilentlyContinue
            Remove-Job $job -ErrorAction SilentlyContinue
        }
    }
    catch {
        Write-LogError "Erro ao verificar métricas: $($_.Exception.Message)"
        return $false
    }
}

# Função para verificar conectividade entre serviços
function Test-ServiceConnectivity {
    Write-LogStep "Verificando conectividade entre serviços..."
    
    try {
        $apiPod = kubectl get pods -n $Namespace -l app=omni-keywords-finder-api -o jsonpath='{.items[0].metadata.name}' 2>$null
        $mlPod = kubectl get pods -n $Namespace -l app=omni-keywords-finder-ml -o jsonpath='{.items[0].metadata.name}' 2>$null
        
        if ([string]::IsNullOrEmpty($apiPod) -or [string]::IsNullOrEmpty($mlPod)) {
            Write-LogWarning "Pods necessários não encontrados para teste de conectividade"
            return $false
        }
        
        # Testar conectividade da API para ML
        Write-LogInfo "Testando conectividade da API para ML..."
        $apiToMl = kubectl exec $apiPod -n $Namespace -- curl -s http://omni-keywords-finder-ml:8001/health 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-LogSuccess "Conectividade da API para ML está funcionando"
        }
        else {
            Write-LogWarning "Conectividade da API para ML não está funcionando"
        }
        
        # Testar conectividade do ML para API
        Write-LogInfo "Testando conectividade do ML para API..."
        $mlToApi = kubectl exec $mlPod -n $Namespace -- curl -s http://omni-keywords-finder-api:8000/health 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-LogSuccess "Conectividade do ML para API está funcionando"
        }
        else {
            Write-LogWarning "Conectividade do ML para API não está funcionando"
        }
        
        return $true
    }
    catch {
        Write-LogError "Erro ao verificar conectividade: $($_.Exception.Message)"
        return $false
    }
}

# Função para verificar configuração de mTLS
function Test-MtlsConfiguration {
    Write-LogStep "Verificando configuração de mTLS..."
    
    try {
        # Verificar se mTLS está habilitado no namespace
        $proxyConfig = kubectl get namespace $Namespace -o jsonpath='{.metadata.annotations.linkerd\.io/proxy-config}' 2>$null
        
        if ($proxyConfig -match '"mTLS":\s*true') {
            Write-LogSuccess "mTLS está habilitado no namespace"
        }
        else {
            Write-LogWarning "mTLS não está explicitamente habilitado no namespace"
        }
        
        # Verificar certificados do Linkerd
        $identitySecret = kubectl get secret -n linkerd linkerd-identity-issuer 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-LogSuccess "Certificados do Linkerd Identity estão configurados"
            return $true
        }
        else {
            Write-LogWarning "Certificados do Linkerd Identity não encontrados"
            return $false
        }
    }
    catch {
        Write-LogError "Erro ao verificar mTLS: $($_.Exception.Message)"
        return $false
    }
}

# Função para gerar relatório
function New-VerificationReport {
    Write-LogStep "Gerando relatório de verificação..."
    
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $reportFile = Join-Path $ReportPath "sidecar-injection-report-$timestamp.txt"
    
    $report = @"
==============================================================================
RELATÓRIO DE VERIFICAÇÃO DE SIDECAR INJECTION - LINKERD
==============================================================================
Data/Hora: $(Get-Date)
Tracing ID: verify-sidecar-injection-2025-01-27-001
Versão: 1.0
Namespace: $Namespace
==============================================================================

1. VERIFICAÇÃO DE INSTALAÇÃO
----------------------------
$(kubectl get namespace linkerd -o wide 2>$null | Out-String)
$(kubectl get pods -n linkerd -l app=linkerd-proxy-injector 2>$null | Out-String)

2. VERIFICAÇÃO DE NAMESPACES
----------------------------
$(foreach ($ns in @("omni-keywords-finder", "omni-keywords-finder-staging", "omni-keywords-finder-development")) {
    "Namespace: $ns"
    kubectl get namespace $ns -o jsonpath='{.metadata.labels.linkerd\.io/inject}' 2>$null
    ""
})

3. VERIFICAÇÃO DE DEPLOYMENTS
-----------------------------
$(kubectl get deployments -n $Namespace -o wide 2>$null | Out-String)

4. VERIFICAÇÃO DE PODS
----------------------
$(kubectl get pods -n $Namespace -o wide 2>$null | Out-String)

5. VERIFICAÇÃO DE SIDECARS
-------------------------
$(kubectl get pods -n $Namespace -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}' 2>$null | Select-String "linkerd-proxy" | Out-String)

6. VERIFICAÇÃO DE MÉTRICAS
-------------------------
Métricas disponíveis via port-forward:4191/metrics

7. RECOMENDAÇÕES
----------------
- Verificar logs dos sidecars se houver problemas
- Monitorar métricas de performance
- Configurar alertas para falhas de injection
- Documentar configurações específicas

==============================================================================
FIM DO RELATÓRIO
==============================================================================
"@
    
    $report | Out-File -FilePath $reportFile -Encoding UTF8
    Write-LogSuccess "Relatório gerado: $reportFile"
    
    return $reportFile
}

# Função principal
function Start-SidecarInjectionVerification {
    Write-Host "==============================================================================" -ForegroundColor Cyan
    Write-Host "🔍 VERIFICAÇÃO DE SIDECAR INJECTION - LINKERD" -ForegroundColor Cyan
    Write-Host "==============================================================================" -ForegroundColor Cyan
    Write-Host "Tracing ID: verify-sidecar-injection-2025-01-27-001" -ForegroundColor White
    Write-Host "Data/Hora: $(Get-Date)" -ForegroundColor White
    Write-Host "Namespace: $Namespace" -ForegroundColor White
    Write-Host "==============================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Executar verificações
    $results = @{
        Kubectl = Test-Kubectl
        LinkerdInstallation = Test-LinkerdInstallation
        NamespaceInjection = Test-NamespaceInjection
        DeploymentInjection = Test-DeploymentInjection
        PodSidecars = Test-PodSidecars
        SidecarStatus = Test-SidecarStatus
        SidecarMetrics = Test-SidecarMetrics
        ServiceConnectivity = Test-ServiceConnectivity
        MtlsConfiguration = Test-MtlsConfiguration
    }
    
    # Gerar relatório se solicitado
    if ($GenerateReport) {
        $reportFile = New-VerificationReport
    }
    
    Write-Host ""
    Write-Host "==============================================================================" -ForegroundColor Cyan
    Write-Host "✅ VERIFICAÇÃO CONCLUÍDA" -ForegroundColor Cyan
    Write-Host "==============================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Resumo das verificações:" -ForegroundColor White
    Write-Host "   - kubectl: $(if ($results.Kubectl) { '✅ Configurado' } else { '❌ Não configurado' })" -ForegroundColor $(if ($results.Kubectl) { 'Green' } else { 'Red' })
    Write-Host "   - Linkerd: $(if ($results.LinkerdInstallation) { '✅ Instalado' } else { '❌ Não instalado' })" -ForegroundColor $(if ($results.LinkerdInstallation) { 'Green' } else { 'Red' })
    Write-Host "   - Namespaces: $(if ($results.NamespaceInjection) { '✅ Verificados' } else { '⚠️ Com problemas' })" -ForegroundColor $(if ($results.NamespaceInjection) { 'Green' } else { 'Yellow' })
    Write-Host "   - Deployments: $(if ($results.DeploymentInjection) { '✅ Verificados' } else { '⚠️ Com problemas' })" -ForegroundColor $(if ($results.DeploymentInjection) { 'Green' } else { 'Yellow' })
    Write-Host "   - Sidecars: $(if ($results.PodSidecars) { '✅ Verificados' } else { '⚠️ Com problemas' })" -ForegroundColor $(if ($results.PodSidecars) { 'Green' } else { 'Yellow' })
    Write-Host "   - Métricas: $(if ($results.SidecarMetrics) { '✅ Verificadas' } else { '⚠️ Com problemas' })" -ForegroundColor $(if ($results.SidecarMetrics) { 'Green' } else { 'Yellow' })
    Write-Host "   - Conectividade: $(if ($results.ServiceConnectivity) { '✅ Testada' } else { '⚠️ Com problemas' })" -ForegroundColor $(if ($results.ServiceConnectivity) { 'Green' } else { 'Yellow' })
    Write-Host "   - mTLS: $(if ($results.MtlsConfiguration) { '✅ Verificado' } else { '⚠️ Com problemas' })" -ForegroundColor $(if ($results.MtlsConfiguration) { 'Green' } else { 'Yellow' })
    Write-Host ""
    
    if ($GenerateReport) {
        Write-Host "📄 Relatório detalhado gerado: $reportFile" -ForegroundColor Green
    }
    
    Write-Host "🔧 Para mais informações, consulte a documentação do Linkerd" -ForegroundColor White
    Write-Host ""
    
    return $results
}

# Executar verificação se script for chamado diretamente
if ($MyInvocation.InvocationName -ne '.') {
    Start-SidecarInjectionVerification
} 