import { useState } from 'react';
import InputCard from './components/InputCard';
import ResultsCard from './components/ResultsCard';
import Spinner from './components/Spinner';
import ToastContainer, { ToastMessage } from './components/ToastContainer';
import { fetchRepo, analyzeRepo } from './api/client';
import { Github } from 'lucide-react';

interface AnalysisReport {
  total_packages: number;
  outdated_count: number;
  health_score: number;
  partial_analysis?: boolean;
  outdated_packages?: Array<{
    name: string;
    current_version: string;
    latest_version: string;
  }>;
}

const STORAGE_KEY = 'deadrepo_last_url';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [lastUrl, setLastUrl] = useState(() => localStorage.getItem(STORAGE_KEY) || '');

  const addToast = (message: string, type: ToastMessage['type'] = 'info') => {
    const id = Date.now().toString();
    setToasts((prev) => [...prev, { id, message, type }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  const handleAnalyze = async (repoUrl: string) => {
    setIsLoading(true);
    setReport(null);
    setLoadingMessage('Cloning repository...');

    try {
      localStorage.setItem(STORAGE_KEY, repoUrl);
      setLastUrl(repoUrl);

      // Step 1 — fetch repo
      const localPath = await fetchRepo(repoUrl);

      // Step 2 — analyze
      setLoadingMessage('Analyzing dependencies...');
      const analysisReport = await analyzeRepo(localPath);

      setReport(analysisReport);
      addToast('Analysis complete!', 'success');
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Something failed';
      addToast(msg, 'error');
      console.error(err);
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-primary to-accent rounded-lg neon-glow-primary">
              <Github className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                DeadRepo Doctor
              </h1>
              <p className="text-sm text-muted-foreground">
                Diagnose your repository's dependency health
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="space-y-8">
          <InputCard 
            onAnalyze={handleAnalyze} 
            isLoading={isLoading}
            initialValue={lastUrl}
          />

          {isLoading && (
            <div className="glass-card rounded-lg p-12 flex justify-center">
              <Spinner size="lg" message={loadingMessage} />
            </div>
          )}

          {report && !isLoading && <ResultsCard report={report} />}
        </div>
      </main>

      <footer className="border-t border-border/50 mt-16">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-muted-foreground">
          <p>Built with React, TypeScript & TailwindCSS · v2</p>
        </div>
      </footer>

      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}

export default App;
