import React, { useState, useEffect } from 'react';
import {
  Clock,
  ShieldCheck,
  FileText,
  Upload,
  CheckCircle2,
  AlertCircle,
  FileCheck,
  RotateCcw,
  Download,
  ChevronDown,
  ChevronRight,
  UserCheck,
} from 'lucide-react';
import { AuditEventItem } from '../types';
import { api } from '../api/client';

interface AuditTimelineProps {
  inspectionId: string;
  initialEvents?: AuditEventItem[];
  className?: string;
}

function formatTimestamp(iso: string) {
  const d = new Date(iso);
  return {
    date: d.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    }),
    time: d.toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }),
  };
}

function getEventIcon(eventType: string) {
  switch (eventType) {
    case 'INSPECTION_CREATED':
      return <FileText className="w-4 h-4 text-blue-600" />;
    case 'EVIDENCE_UPLOADED':
    case 'EVIDENCE_ACCEPTED':
      return <Upload className="w-4 h-4 text-indigo-600" />;
    case 'IMAGE_QUALITY_ASSESSED':
    case 'OCR_PROCESSED':
    case 'DECLARATIONS_EXTRACTED':
    case 'APPLICABILITY_EVALUATED':
    case 'COMPLIANCE_EVALUATED':
      return <ShieldCheck className="w-4 h-4 text-emerald-600" />;
    case 'DECLARATION_CORRECTED':
    case 'DECLARATION_MANUALLY_CORRECTED':
    case 'MANUAL_OBSERVATION_RECORDED':
      return <FileCheck className="w-4 h-4 text-amber-600" />;
    case 'INSPECTION_SUBMITTED_FOR_REVIEW':
    case 'VERIFICATION_SUBMITTED':
      return <UserCheck className="w-4 h-4 text-purple-600" />;
    case 'REVIEW_REVISION_REQUESTED':
      return <RotateCcw className="w-4 h-4 text-rose-600" />;
    case 'REVIEWER_DECISION_RECORDED':
      return <CheckCircle2 className="w-4 h-4 text-teal-600" />;
    case 'REVIEWER_OVERRIDE_RECORDED':
      return <AlertCircle className="w-4 h-4 text-orange-600" />;
    case 'INSPECTION_FINALIZED':
      return <ShieldCheck className="w-4 h-4 text-emerald-700 font-bold" />;
    case 'REPORT_DOWNLOADED':
      return <Download className="w-4 h-4 text-slate-600" />;
    default:
      return <Clock className="w-4 h-4 text-slate-500" />;
  }
}

function getEventBadgeColor(eventType: string): string {
  if (eventType.includes('FINALIZED')) return 'bg-emerald-50 text-emerald-700 border-emerald-200';
  if (eventType.includes('OVERRIDE')) return 'bg-orange-50 text-orange-700 border-orange-200';
  if (eventType.includes('REVISION')) return 'bg-rose-50 text-rose-700 border-rose-200';
  if (eventType.includes('CORRECTED')) return 'bg-amber-50 text-amber-700 border-amber-200';
  if (eventType.includes('SUBMITTED')) return 'bg-purple-50 text-purple-700 border-purple-200';
  if (eventType.includes('DOWNLOADED')) return 'bg-slate-100 text-slate-700 border-slate-200';
  return 'bg-blue-50 text-blue-700 border-blue-200';
}

export const AuditTimeline: React.FC<AuditTimelineProps> = ({
  inspectionId,
  initialEvents,
  className = '',
}) => {
  const [events, setEvents] = useState<AuditEventItem[]>(initialEvents || []);
  const [loading, setLoading] = useState(!initialEvents);
  const [error, setError] = useState<string | null>(null);
  const [expandedEvents, setExpandedEvents] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (initialEvents && initialEvents.length > 0) {
      setEvents(initialEvents);
      return;
    }

    let isMounted = true;
    const fetchTimeline = async () => {
      try {
        setLoading(true);
        const data = await api.getAuditTrail(inspectionId);
        if (isMounted) {
          setEvents(data);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to load audit chain-of-custody.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchTimeline();
    return () => {
      isMounted = false;
    };
  }, [inspectionId, initialEvents]);

  const toggleExpand = (id: string) => {
    setExpandedEvents((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  if (loading) {
    return (
      <div className={`p-6 bg-white border border-slate-200 rounded-lg text-center ${className}`}>
        <div className="flex items-center justify-center space-x-2 text-slate-400 text-sm">
          <div className="w-4 h-4 border-2 border-slate-200 border-t-slate-600 rounded-full animate-spin" />
          <span>Loading immutable audit chain-of-custody…</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 ${className}`}>
        {error}
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className={`p-6 bg-white border border-slate-200 rounded-lg text-center text-slate-500 text-sm ${className}`}>
        <Clock className="w-6 h-6 text-slate-300 mx-auto mb-2" />
        No audit events recorded for this inspection docket.
      </div>
    );
  }

  return (
    <div className={`bg-white border border-slate-200 rounded-lg p-5 shadow-[0_1px_2px_rgba(15,23,42,0.05)] ${className}`}>
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div>
          <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-blue-700" />
            Audit Trail & Chain of Custody
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Immutable chronological ledger of regulatory actions ({events.length} recorded events)
          </p>
        </div>
        <span className="text-[11px] font-mono text-slate-400 bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
          APPEND-ONLY
        </span>
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[2px] before:bg-slate-200">
        {events.map((ev, index) => {
          const { date, time } = formatTimestamp(ev.created_at);
          const isExpanded = expandedEvents[ev.id];
          const hasDetails = ev.details && Object.keys(ev.details).length > 0;

          return (
            <div key={ev.id || index} className="relative group">
              {/* Timeline Bullet */}
              <div className="absolute -left-6 top-0.5 w-6 h-6 rounded-full bg-white border border-slate-300 flex items-center justify-center shadow-xs">
                {getEventIcon(ev.event_type)}
              </div>

              {/* Event Card */}
              <div className="bg-slate-50 hover:bg-slate-100/80 transition-colors border border-slate-200 rounded-lg p-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <span className={`text-[11px] font-semibold px-2 py-0.5 rounded border font-mono ${getEventBadgeColor(ev.event_type)}`}>
                      {ev.event_type}
                    </span>
                    {ev.actor_role && (
                      <span className="text-[10px] uppercase font-bold text-slate-500 bg-slate-200/70 px-1.5 py-0.5 rounded">
                        {ev.actor_role}
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] font-mono text-slate-500 flex items-center gap-1.5">
                    <span>{date}</span>
                    <span className="text-slate-300">•</span>
                    <span>{time}</span>
                  </div>
                </div>

                <div className="mt-1.5 flex items-center justify-between text-xs text-slate-600">
                  <div>
                    {ev.actor_id && (
                      <span className="font-mono text-[11px] text-slate-500">
                        Actor: {ev.actor_id}
                      </span>
                    )}
                  </div>
                  {hasDetails && (
                    <button
                      onClick={() => toggleExpand(ev.id)}
                      className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1 cursor-pointer"
                    >
                      {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                      {isExpanded ? 'Hide Payload' : 'View Payload'}
                    </button>
                  )}
                </div>

                {/* Expandable Structured Payload */}
                {isExpanded && hasDetails && (
                  <div className="mt-2.5 pt-2 border-t border-slate-200/80">
                    <pre className="text-[11px] font-mono bg-white p-2.5 rounded border border-slate-200 overflow-x-auto text-slate-700 leading-relaxed">
                      {JSON.stringify(ev.details, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
