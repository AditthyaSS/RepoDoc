import { useState } from 'react';
import { Package, AlertTriangle, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react';
import HealthScoreRing from './HealthScoreRing';

interface OutdatedPackage {
  name: string;
  current_version: string;
  latest_version: string;
}

interface AnalysisReport {
  total_packages: number;
  outdated_count: number;
  health_score: number;
  partial_analysis?: boolean;
  outdated_packages?: OutdatedPackage[];
}

interface ResultsCardProps {
  report: AnalysisReport;
}

export default function ResultsCard({ report }: ResultsCardProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  
  const hasOutdated = (report.outdated_packages?.length || 0) > 0;
  const upToDateCount = report.total_packages - report.outdated_count;

  return (
    <div className="glass-card rounded-lg p-8 animate-fade-in space-y-6">
      {/* Header with Health Score */}
      <div className="flex flex-col md:flex-row items-center gap-6 md:gap-8">
        <HealthScoreRing score={report.health_score} />
        
        <div className="flex-1 text-center md:text-left">
          <h2 className="text-2xl font-bold mb-2">Analysis Complete</h2>
          <p className="text-muted-foreground">
            Repository dependency health assessment
          </p>
          
          {report.partial_analysis && (
            <div className="mt-3 flex items-center gap-2 text-warning text-sm">
              <AlertTriangle className="w-4 h-4" />
              <span>Partial analysis - large repository</span>
            </div>
          )}
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-input rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-foreground mb-1">
            {report.total_packages}
          </div>
          <div className="text-sm text-muted-foreground flex items-center justify-center gap-1">
            <Package className="w-4 h-4" />
            Total Packages
          </div>
        </div>

        <div className="glass-input rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-success mb-1">
            {upToDateCount}
          </div>
          <div className="text-sm text-muted-foreground flex items-center justify-center gap-1">
            <CheckCircle className="w-4 h-4" />
            Up to Date
          </div>
        </div>

        <div className="glass-input rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-destructive mb-1">
            {report.outdated_count}
          </div>
          <div className="text-sm text-muted-foreground flex items-center justify-center gap-1">
            <AlertTriangle className="w-4 h-4" />
            Outdated
          </div>
        </div>
      </div>

      {/* Outdated Packages List */}
      {hasOutdated && (
        <div className="border-t border-border pt-6">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="w-full flex items-center justify-between text-left mb-4 hover:text-primary transition-colors"
            aria-expanded={isExpanded}
          >
            <h3 className="text-lg font-semibold">
              Outdated Packages ({report.outdated_packages!.length})
            </h3>
            {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>

          {isExpanded && (
            <div className="space-y-2 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
              {report.outdated_packages!.map((pkg, index) => (
                <div
                  key={`${pkg.name}-${index}`}
                  className="glass-input rounded-lg p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:border-primary/30 transition-colors"
                >
                  <div className="flex-1">
                    <h4 className="font-mono font-semibold text-foreground">
                      {pkg.name}
                    </h4>
                  </div>
                  
                  <div className="flex items-center gap-3 text-sm">
                    <span className="px-3 py-1 rounded-full bg-destructive/10 text-destructive border border-destructive/20">
                      {pkg.current_version}
                    </span>
                    <span className="text-muted-foreground">→</span>
                    <span className="px-3 py-1 rounded-full bg-success/10 text-success border border-success/20">
                      {pkg.latest_version}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {!hasOutdated && report.outdated_count === 0 && (
        <div className="text-center py-8">
          <CheckCircle className="w-16 h-16 text-success mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-success mb-2">
            All Dependencies Up to Date!
          </h3>
          <p className="text-muted-foreground">
            Your repository has no outdated packages.
          </p>
        </div>
      )}
    </div>
  );
}
