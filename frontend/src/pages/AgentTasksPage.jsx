import React, { useState, useEffect } from 'react';
import { Bot, Plus, ShieldCheck } from 'lucide-react';
import { AgentWorkflow } from '../components/agent/AgentWorkflow';
import { Modal } from '../components/common/Modal';
import { getAgentTasks, createAgentTask } from '../services/api';

export const AgentTasksPage = () => {
  const [tasks, setTasks] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [taskForm, setTaskForm] = useState({
    title: 'Vessel Hydro-Test Safety Audit',
    sourceDocument: 'Safety_SOP_2025.pdf',
    outputFormat: 'DOCX Approval Note',
  });

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    const data = await getAgentTasks();
    setTasks(data);
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();

    try {
      const newTask = await createAgentTask(taskForm);

      // Add the real backend result directly to the page
      setTasks((previousTasks) => [newTask, ...previousTasks]);

      // Close the modal
      setIsModalOpen(false);

    } catch (error) {
      console.error('Failed to create agent task:', error);
      alert('Failed to start agent task. Please check whether the backend is running.');
    }
  };

  return (
    <div className="p-6 space-y-6">

      {/* Page Header */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">

        <div>
          <div className="flex items-center gap-2">
            <Bot className="w-6 h-6 text-cyan-400" />

            <h2 className="text-xl font-bold text-slate-100">
              Agentic Workflow Runner
            </h2>
          </div>

          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Autonomous local multi-agent system executing 6-stage industrial workflows:
            Plan → Retrieve → Analyze → Execute → Verify → Deliver.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-cyan-500/10 cursor-pointer"
        >
          <Plus className="w-4 h-4 stroke-[3]" />
          <span>Create New Agent Task</span>
        </button>

      </div>

      {/* Pipeline Stage Explanation Legend */}
      <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400 font-mono">

        <span className="font-bold text-slate-200 uppercase tracking-wider">
          Autonomous Stages:
        </span>

        <div className="flex flex-wrap items-center gap-2">

          {[
            '1. Plan',
            '2. Retrieve',
            '3. Analyze',
            '4. Execute',
            '5. Verify',
            '6. Deliver'
          ].map((stage, idx) => (
            <span
              key={idx}
              className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-cyan-300"
            >
              {stage}
            </span>
          ))}

        </div>
      </div>

      {/* Agent Workflows */}
      <div className="space-y-6">

        {tasks.map((task) => (
          <AgentWorkflow
            key={task.id}
            task={task}
          />
        ))}

      </div>

      {/* Create Agent Task Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Launch Autonomous Agent Task"
      >

        <form
          onSubmit={handleCreateTask}
          className="space-y-4"
        >

          {/* Task Title */}
          <div>

            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">
              Task Title
            </label>

            <input
              type="text"
              value={taskForm.title}
              onChange={(e) =>
                setTaskForm({
                  ...taskForm,
                  title: e.target.value
                })
              }
              className="w-full bg-slate-950 text-slate-100 text-xs rounded-lg p-2.5 border border-slate-800 focus:outline-none focus:border-cyan-500"
              required
            />

          </div>

          {/* Source Document */}
          <div>

            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">
              Source Input Document
            </label>

            <select
              value={taskForm.sourceDocument}
              onChange={(e) =>
                setTaskForm({
                  ...taskForm,
                  sourceDocument: e.target.value
                })
              }
              className="w-full bg-slate-950 text-slate-100 text-xs rounded-lg p-2.5 border border-slate-800 focus:outline-none focus:border-cyan-500"
            >

              <option value="Inspection_Report_Turbine_A.pdf">
                Inspection_Report_Turbine_A.pdf
              </option>

              <option value="Safety_SOP_2025.pdf">
                Safety_SOP_2025.pdf
              </option>

              <option value="Maintenance_Manual_Refinery_V3.pdf">
                Maintenance_Manual_Refinery_V3.pdf
              </option>

            </select>

          </div>

          {/* Output Format */}
          <div>

            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">
              Target Output Deliverable
            </label>

            <select
              value={taskForm.outputFormat}
              onChange={(e) =>
                setTaskForm({
                  ...taskForm,
                  outputFormat: e.target.value
                })
              }
              className="w-full bg-slate-950 text-slate-100 text-xs rounded-lg p-2.5 border border-slate-800 focus:outline-none focus:border-cyan-500"
            >

              <option value="DOCX Approval Note">
                DOCX Approval Note
              </option>

              <option value="PDF Technical Audit Summary">
                PDF Technical Audit Summary
              </option>

              <option value="XLSX Compliance Matrix">
                XLSX Compliance Matrix
              </option>

            </select>

          </div>

          {/* Local AI Notice */}
          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-[11px] text-emerald-400">

            <ShieldCheck className="w-4 h-4 inline mr-1" />

            Agent task will run locally using the Sovereign AI backend.

          </div>

          {/* Buttons */}
          <div className="flex justify-end gap-2 pt-2">

            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700"
            >
              Cancel
            </button>

            <button
              type="submit"
              className="px-4 py-2 rounded-lg bg-cyan-500 text-slate-950 font-bold text-xs hover:bg-cyan-400"
            >
              Start Agent Task
            </button>

          </div>

        </form>

      </Modal>

    </div>
  );
};