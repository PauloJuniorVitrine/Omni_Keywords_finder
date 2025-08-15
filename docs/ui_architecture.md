# Arquitetura de UI

Este documento detalha a arquitetura de UI do Omni Keywords Finder.

## Componentes

### Layout
```typescript
// components/Layout/index.tsx
interface LayoutProps {
  children: React.ReactNode;
  title?: string;
}

const Layout: React.FC<LayoutProps> = ({ children, title }) => {
  return (
    <div className="layout">
      <Header />
      <Sidebar />
      <main className="content">
        {title && <h1>{title}</h1>}
        {children}
      </main>
      <Footer />
    </div>
  );
};
```

### Keywords
```typescript
// components/Keywords/KeywordForm.tsx
interface KeywordFormProps {
  onSubmit: (keyword: Keyword) => void;
  onCancel: () => void;
}

const KeywordForm: React.FC<KeywordFormProps> = ({ onSubmit, onCancel }) => {
  const [form, setForm] = useState<KeywordFormData>({
    text: "",
    volume: 0,
    difficulty: 0.5,
    language: "pt"
  });

  return (
    <form onSubmit={handleSubmit}>
      <TextField
        label="Texto"
        value={form.text}
        onChange={handleChange}
      />
      <NumberField
        label="Volume"
        value={form.volume}
        onChange={handleChange}
      />
      <Slider
        label="Dificuldade"
        value={form.difficulty}
        onChange={handleChange}
      />
      <Select
        label="Idioma"
        value={form.language}
        onChange={handleChange}
        options={[
          { value: "pt", label: "Português" },
          { value: "en", label: "English" }
        ]}
      />
      <ButtonGroup>
        <Button type="submit">Salvar</Button>
        <Button onClick={onCancel}>Cancelar</Button>
      </ButtonGroup>
    </form>
  );
};
```

### Clusters
```typescript
// components/Clusters/ClusterView.tsx
interface ClusterViewProps {
  cluster: Cluster;
  onEdit?: (cluster: Cluster) => void;
  onDelete?: (id: string) => void;
}

const ClusterView: React.FC<ClusterViewProps> = ({
  cluster,
  onEdit,
  onDelete
}) => {
  return (
    <Card>
      <CardHeader title={cluster.name} />
      <CardContent>
        <KeywordList keywords={cluster.keywords} />
        <ScoreBadge score={cluster.score} />
      </CardContent>
      <CardActions>
        {onEdit && (
          <Button onClick={() => onEdit(cluster)}>
            Editar
          </Button>
        )}
        {onDelete && (
          <Button onClick={() => onDelete(cluster.id)}>
            Excluir
          </Button>
        )}
      </CardActions>
    </Card>
  );
};
```

## Páginas

### Dashboard
```typescript
// pages/Dashboard/index.tsx
const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    keywords: 0,
    clusters: 0,
    users: 0
  });

  return (
    <Layout title="Dashboard">
      <StatsGrid stats={stats} />
      <RecentActivity />
      <PerformanceChart />
    </Layout>
  );
};
```

### Keywords
```typescript
// pages/Keywords/index.tsx
const KeywordsPage: React.FC = () => {
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [filters, setFilters] = useState<KeywordFilters>({
    language: "pt",
    minVolume: 0,
    maxDifficulty: 1
  });

  return (
    <Layout title="Keywords">
      <FilterBar filters={filters} onChange={setFilters} />
      <KeywordList keywords={keywords} />
      <Pagination />
    </Layout>
  );
};
```

## Estado

### Context
```typescript
// context/AppContext.tsx
interface AppContextData {
  user: User | null;
  theme: Theme;
  setTheme: (theme: Theme) => void;
  logout: () => void;
}

const AppContext = createContext<AppContextData>({} as AppContextData);

export const AppProvider: React.FC = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [theme, setTheme] = useState<Theme>("light");

  return (
    <AppContext.Provider value={{
      user,
      theme,
      setTheme,
      logout: () => setUser(null)
    }}>
      {children}
    </AppContext.Provider>
  );
};
```

## Estilos

### Tema
```typescript
// styles/theme.ts
const theme = {
  colors: {
    primary: "#2196f3",
    secondary: "#f50057",
    background: "#ffffff",
    text: "#000000"
  },
  typography: {
    fontFamily: "Roboto, sans-serif",
    h1: {
      fontSize: "2.5rem",
      fontWeight: 500
    },
    body1: {
      fontSize: "1rem",
      lineHeight: 1.5
    }
  },
  spacing: {
    xs: "0.25rem",
    sm: "0.5rem",
    md: "1rem",
    lg: "2rem"
  }
};
```

## Observações

1. Componentes reutilizáveis
2. Estado centralizado
3. Tipagem forte
4. Tema consistente
5. Responsividade
6. Acessibilidade
7. Performance
8. Testes
9. Documentação
10. Manutenibilidade 