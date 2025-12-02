import { useState } from 'react';
import { Github, X } from 'lucide-react';

interface InputCardProps {
  onAnalyze: (repoUrl: string) => void;
  isLoading: boolean;
  initialValue?: string;
}

export default function InputCard({ onAnalyze, isLoading, initialValue = '' }: InputCardProps) {
  const [repoUrl, setRepoUrl] = useState(initialValue);
  const [error, setError] = useState('');

  const validateUrl = (url: string): boolean => {
    if (!url.trim()) {
      setError('Please enter a repository URL');
      return false;
    }

    if (!url.includes('github.com')) {
      setError('Please enter a valid GitHub repository URL');
      return false;
    }

    setError('');
    return true;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateUrl(repoUrl) && !isLoading) {
      onAnalyze(repoUrl);
    }
  };

  const handleClear = () => {
    setRepoUrl('');
    setError('');
  };

  return (
    <div className="glass-card rounded-lg p-8 animate-fade-in">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-primary/10 rounded-lg">
          <Github className="w-6 h-6 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Analyze Repository</h2>
          <p className="text-sm text-muted-foreground">Enter a GitHub repository URL to check dependency health</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/username/repository"
            disabled={isLoading}
            className="glass-input w-full px-4 py-3 pr-10 rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="GitHub repository URL"
            aria-invalid={!!error}
            aria-describedby={error ? 'url-error' : undefined}
          />
          {repoUrl && !isLoading && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              aria-label="Clear input"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {error && (
          <p id="url-error" className="text-sm text-destructive" role="alert">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-primary to-accent px-6 py-3 rounded-lg font-semibold text-primary-foreground hover:shadow-lg hover:shadow-primary/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none"
        >
          {isLoading ? 'Analyzing...' : 'Fetch & Analyze'}
        </button>
      </form>
    </div>
  );
}
