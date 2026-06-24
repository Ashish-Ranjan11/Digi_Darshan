"use client";

import { useEffect, useState } from "react";
import { apiFetch, formatDate } from "@/lib/api";

type ActionTemplate = {
  action_type: string;
  label: string;
  title: string;
  instruction: string;
  severity: string;
  location?: string;
};

type ControlAction = {
  id: number;
  temple_id: number;
  action_type: string;
  title: string;
  instruction: string;
  severity: string;
  location?: string;
  status: string;
  created_by_id?: number;
  created_at: string;
  resolved_at?: string;
  temple_name?: string;
  created_by_name?: string;
};

function severityClass(severity: string) {
  if (severity === "critical") {
    return "border-red-200 bg-red-50 text-red-700";
  }

  if (severity === "warning") {
    return "border-orange-200 bg-orange-50 text-orange-700";
  }

  return "border-blue-200 bg-blue-50 text-blue-700";
}

function statusClass(status: string) {
  if (status === "resolved") {
    return "bg-green-100 text-green-700";
  }

  return "bg-red-100 text-red-700";
}

export default function ControlActionPanel({
  templeId,
  onActionDone,
}: {
  templeId: number;
  onActionDone?: () => void;
}) {
  const [templates, setTemplates] = useState<ActionTemplate[]>([]);
  const [actions, setActions] = useState<ControlAction[]>([]);
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [message, setMessage] = useState("");

  async function load() {
    const [templateData, actionData] = await Promise.all([
      apiFetch<ActionTemplate[]>("/api/control-actions/templates"),
      apiFetch<ControlAction[]>(`/api/control-actions/${templeId}`),
    ]);

    setTemplates(templateData);
    setActions(actionData);
  }

  async function triggerAction(template: ActionTemplate) {
    setLoadingAction(template.action_type);
    setMessage("");

    try {
      await apiFetch<ControlAction>("/api/control-actions", {
        method: "POST",
        body: JSON.stringify({
          temple_id: templeId,
          action_type: template.action_type,
        }),
      });

      setMessage(`${template.label} activated and broadcasted.`);
      await load();
      onActionDone?.();
    } catch (err: any) {
      setMessage(err.message || "Unable to trigger control action");
    } finally {
      setLoadingAction(null);
    }
  }

  async function resolveAction(actionId: number) {
    setMessage("");

    try {
      await apiFetch<ControlAction>(`/api/control-actions/${actionId}/resolve`, {
        method: "PATCH",
      });

      setMessage("Control action resolved.");
      await load();
      onActionDone?.();
    } catch (err: any) {
      setMessage(err.message || "Unable to resolve action");
    }
  }

  useEffect(() => {
    load().catch((err) => setMessage(err.message));
  }, [templeId]);

  const activeActions = actions.filter((action) => action.status === "active");
  const recentActions = actions.slice(0, 8);

  return (
    <div className="space-y-5">
      <div className="card p-6">
        <div>
          <p className="font-black uppercase tracking-widest text-orange-600">
            Digii-Command Center
          </p>

          <h2 className="mt-1 text-2xl font-black text-temple">
            One-Click Crowd Control Actions
          </h2>

          <p className="mt-1 text-sm text-gray-600">
            Trigger official control-room actions, broadcast pilgrim alerts, and
            log emergency decisions.
          </p>
        </div>

        {message ? (
          <p className="mt-5 rounded-2xl bg-orange-50 p-3 text-sm font-bold text-orange-800">
            {message}
          </p>
        ) : null}

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {templates.map((template) => (
            <button
              key={template.action_type}
              onClick={() => triggerAction(template)}
              disabled={loadingAction === template.action_type}
              className={`rounded-3xl border p-4 text-left transition hover:scale-[1.01] hover:shadow-md disabled:cursor-not-allowed disabled:opacity-60 ${severityClass(
                template.severity
              )}`}
            >
              <div className="flex items-center justify-between gap-3">
                <h3 className="font-black">{template.label}</h3>

                <span className="rounded-full bg-white px-3 py-1 text-xs font-black uppercase">
                  {template.severity}
                </span>
              </div>

              <p className="mt-2 text-sm font-semibold">{template.title}</p>

              <p className="mt-1 text-xs opacity-90">
                {template.instruction}
              </p>

              <p className="mt-3 text-xs font-black uppercase">
                {loadingAction === template.action_type
                  ? "Activating..."
                  : "Click to activate"}
              </p>
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card p-6">
          <h3 className="text-xl font-black text-temple">
            Active Command Actions
          </h3>

          <div className="mt-5 space-y-3">
            {activeActions.length === 0 ? (
              <p className="text-sm text-gray-500">
                No active command action right now.
              </p>
            ) : null}

            {activeActions.map((action) => (
              <div
                key={action.id}
                className={`rounded-3xl border p-4 ${severityClass(
                  action.severity
                )}`}
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-xs font-black uppercase">
                      {action.severity} •{" "}
                      {action.location || "Temple Premises"}
                    </p>

                    <h4 className="mt-1 font-black">{action.title}</h4>
                  </div>

                  <span
                    className={`rounded-full px-3 py-1 text-xs font-black uppercase ${statusClass(
                      action.status
                    )}`}
                  >
                    {action.status}
                  </span>
                </div>

                <p className="mt-2 text-sm font-semibold">
                  {action.instruction}
                </p>

                <p className="mt-2 text-xs opacity-80">
                  By {action.created_by_name || "control room"} •{" "}
                  {formatDate(action.created_at)}
                </p>

                <button
                  onClick={() => resolveAction(action.id)}
                  className="btn-secondary mt-4 py-2"
                >
                  Resolve Action
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-xl font-black text-temple">Command History</h3>

          <div className="mt-5 space-y-3">
            {recentActions.length === 0 ? (
              <p className="text-sm text-gray-500">
                No command history available yet.
              </p>
            ) : null}

            {recentActions.map((action) => (
              <div
                key={action.id}
                className="rounded-2xl border border-orange-100 p-4 text-sm"
              >
                <div className="flex items-center justify-between gap-3">
                  <b className="text-temple">{action.title}</b>

                  <span
                    className={`rounded-full px-3 py-1 text-xs font-black uppercase ${statusClass(
                      action.status
                    )}`}
                  >
                    {action.status}
                  </span>
                </div>

                <p className="mt-1 text-gray-600">{action.instruction}</p>

                <p className="mt-2 text-xs text-gray-500">
                  {action.location || "Temple"} •{" "}
                  {formatDate(action.created_at)}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}