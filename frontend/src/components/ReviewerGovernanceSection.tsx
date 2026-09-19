import React from 'react';
import {
  Shield,
  Edit3,
  Scale,
} from 'lucide-react';
import {
  InspectionCase,
  ReviewerDecision,
  ComplianceEvaluationSummary,
  ComplianceFinding,
} from '../types';
import { ComplianceBadge } from './StatusBadge';

interface ReviewerGovernanceSectionProps {
  inspection: InspectionCase;
  reviewerDecisions: ReviewerDecision[];
  complianceSummary: ComplianceEvaluationSummary | null;
  isReadOnly: boolean;
  isReviewer: boolean;
  onOpenAdjudicationDrawer: (finding: ComplianceFinding) => void;
  onOpenFinalizeModal: () => void;
  onOpenRevisionModal: () => void;
}

export const ReviewerGovernanceSection: React.FC<ReviewerGovernanceSectionProps> = ({
  inspection,
  reviewerDecisions,
  complianceSummary,
  isReadOnly,
  isReviewer,
  onOpenAdjudicationDrawer,
  onOpenFinalizeModal,
  onOpenRevisionModal,
}) => {
  const findings = complianceSummary?.findings || [];
  const decisionsMap = new Map<string, ReviewerDecision>();
  reviewerDecisions.forEach((d) => decisionsMap.set(d.requirement_name, d));

  const isSubmitted = inspection.status === 'SUBMITTED_FOR_REVIEW';

  return (
    <div className="p-4 space-y-6">
      {/* Header & Reviewer Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <div className="flex items-center space-x-2">
            <Scale className="w-4 h-4 text-slate-900" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 font-sans">
              Reviewer Governance & Statutory Adjudication
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Independent human reviewer determinations. Automated AI/rule findings are preserved separately from reviewer adjudications.
          </p>
        </div>

        {isReviewer && isSubmitted && !isReadOnly && (
          <div className="flex items-center space-x-2 shrink-0">
            <button
              onClick={onOpenRevisionModal}
              className="px-3 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 text-xs font-semibold rounded transition-colors shadow-2xs"
            >
              Request Revision
            </button>
            <button
              onClick={onOpenFinalizeModal}
              className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded transition-colors shadow-2xs"
            >
              Finalize Docket
            </button>
          </div>
        )}
      </div>

      {/* Governance Model Explainer */}
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs flex items-start space-x-2.5">
        <Shield className="w-4 h-4 text-slate-700 shrink-0 mt-0.5" />
        <div className="text-slate-600 leading-relaxed text-[11px]">
          <strong className="text-slate-900">Statutory Separation Principle:</strong> Automated findings (
          <span className="font-mono text-slate-800 font-medium">Potential Non-Compliance</span>, <span className="font-mono text-slate-800 font-medium">Pass</span>) are generated deterministically and are NEVER overwritten. When a Reviewer adjudicates or overrides an assessment, a separate auditable{' '}
          <span className="font-mono text-slate-900 font-semibold">ReviewerDecision</span> record is created with mandatory statutory rationale.
        </div>
      </div>

      {/* Findings vs Reviewer Decisions Matrix */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
            Statutory Requirements Adjudication ({findings.length} Requirements)
          </h4>
          <span className="text-[11px] font-mono text-slate-500">
            {reviewerDecisions.length} Decisions Recorded
          </span>
        </div>

        {findings.length === 0 ? (
          <div className="bg-white border border-slate-200 border-dashed rounded-lg p-6 text-center text-slate-400 text-xs">
            No compliance evaluation findings available. Please run compliance evaluation first.
          </div>
        ) : (
          <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-2xs">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-50 text-slate-700 font-semibold text-[11px] border-b border-slate-200 uppercase">
                <tr>
                  <th className="py-2.5 px-3 w-28">Rule Citation</th>
                  <th className="py-2.5 px-3 w-48">Requirement</th>
                  <th className="py-2.5 px-3 w-36">System Finding</th>
                  <th className="py-2.5 px-3 w-40">Reviewer Decision</th>
                  <th className="py-2.5 px-3 min-w-[200px]">Reviewer Justification</th>
                  <th className="py-2.5 px-3 w-24 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-sans">
                {findings.map((finding) => {
                  const decision = decisionsMap.get(finding.requirement_name);
                  const isOverridden = decision?.is_override;

                  return (
                    <tr key={finding.id} className="hover:bg-slate-50/70 transition-colors">
                      {/* Rule Citation */}
                      <td className="py-2.5 px-3 font-mono font-bold text-slate-800 whitespace-nowrap align-top">
                        <span className="px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200">
                          {finding.rule_citation}
                        </span>
                      </td>

                      {/* Requirement Name */}
                      <td className="py-2.5 px-3 font-semibold text-slate-900 align-top">
                        <div>{finding.requirement_name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}</div>
                        <div className="text-[10px] text-slate-400 font-mono mt-0.5 font-normal">
                          Eval v{finding.evaluation_version}
                        </div>
                      </td>

                      {/* Automated Finding */}
                      <td className="py-2.5 px-3 align-top whitespace-nowrap">
                        <ComplianceBadge result={finding.result} />
                      </td>

                      {/* Reviewer Determination */}
                      <td className="py-2.5 px-3 align-top whitespace-nowrap">
                        {decision ? (
                          <div className="space-y-1">
                            <ComplianceBadge result={decision.adjudicated_result} />
                            {isOverridden && (
                              <span className="block text-[9px] font-mono px-1.5 py-0.2 bg-amber-50 text-amber-900 border border-amber-300 rounded font-bold w-fit">
                                OVERRIDDEN
                              </span>
                            )}
                          </div>
                        ) : (
                          <span className="text-[11px] text-slate-400 italic">
                            Pending Reviewer
                          </span>
                        )}
                      </td>

                      {/* Reviewer Justification */}
                      <td className="py-2.5 px-3 text-slate-700 leading-snug align-top text-[11px]">
                        {decision ? (
                          <div>
                            <div className="font-medium text-slate-900">{decision.rationale}</div>
                            <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                              {new Date(decision.created_at).toLocaleString()}
                            </div>
                          </div>
                        ) : (
                          <span className="text-slate-400 italic text-[10px]">
                            No separate determination recorded.
                          </span>
                        )}
                      </td>

                      {/* Action */}
                      <td className="py-2.5 px-3 text-right align-top whitespace-nowrap">
                        {isReviewer && !isReadOnly ? (
                          <button
                            onClick={() => onOpenAdjudicationDrawer(finding)}
                            className="inline-flex items-center space-x-1 px-2 py-1 bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 text-[11px] font-semibold rounded transition-colors shadow-2xs"
                          >
                            <Edit3 className="w-3 h-3 text-slate-500" />
                            <span>Adjudicate</span>
                          </button>
                        ) : (
                          <span className="text-[10px] text-slate-400 font-mono">
                            {isReadOnly ? 'LOCKED' : 'REVIEWER ONLY'}
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
