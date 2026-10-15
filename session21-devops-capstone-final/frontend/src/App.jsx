import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Activity, ArrowDownRight, ArrowRight, Bell, CalendarDays, Check,
  CheckCircle2, ChevronDown, CircleDashed, ClipboardList, Clock3,
  Command, Filter, LayoutDashboard, Layers, ListTodo, LoaderCircle,
  MoreHorizontal, Plus, Search, Settings2, ShieldCheck, Trash2, X,
} from 'lucide-react'

const emptyForm = {
  title: '', description: '', status: 'Todo', priority: 'Medium', assignee: '', due_date: '',
}
const statuses = ['All tasks', 'Todo', 'In Progress', 'Done']
const priorities = ['Low', 'Medium', 'High']

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })
  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const body = await response.json()
      detail = body.detail || detail
    } catch { /* response did not contain JSON */ }
    throw new Error(typeof detail === 'string' ? detail : 'Please check the task details.')
  }
  if (response.status === 204) return null
  return response.json()
}

function StatusBadge({ status }) {
  const icon = status === 'Done' ? <CheckCircle2 size={13} /> : status === 'In Progress' ? <Clock3 size={13} /> : <CircleDashed size={13} />
  return <span className={`status-badge status-${status.toLowerCase().replace(' ', '-')}`}>{icon}{status}</span>
}

function PriorityBadge({ priority }) {
  return <span className={`priority priority-${priority.toLowerCase()}`}><span />{priority}</span>
}

function TaskModal({ initial = emptyForm, onClose, onSave, saving }) {
  const [form, setForm] = useState({ ...emptyForm, ...initial, due_date: initial.due_date || '' })
  const [formError, setFormError] = useState('')
  const change = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  const submit = async (event) => {
    event.preventDefault()
    if (!form.title.trim()) {
      setFormError('Add a task title before saving.')
      return
    }
    setFormError('')
    const payload = {
      ...form,
      title: form.title.trim(),
      description: form.description.trim() || null,
      assignee: form.assignee.trim() || null,
      due_date: form.due_date || null,
    }
    try { await onSave(payload) } catch (error) { setFormError(error.message) }
  }

  return (
    <div className="modal-scrim" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div className="modal-top">
          <div><p className="eyebrow">TASK DETAILS</p><h2 id="modal-title">Create a task</h2><p className="muted">Add a clear next step for your team.</p></div>
          <button className="icon-button" onClick={onClose} aria-label="Close dialog"><X size={18} /></button>
        </div>
        <form onSubmit={submit} className="task-form">
          <label>Task title <span className="required">*</span><input autoFocus name="title" value={form.title} onChange={change} placeholder="e.g. Ship the API integration" maxLength={160} /></label>
          <label>Description <textarea name="description" value={form.description} onChange={change} placeholder="Add context, acceptance criteria, or links" rows="3" /></label>
          <div className="form-grid">
            <label>Status<select name="status" value={form.status} onChange={change}>{statuses.slice(1).map((item) => <option key={item}>{item}</option>)}</select></label>
            <label>Priority<select name="priority" value={form.priority} onChange={change}>{priorities.map((item) => <option key={item}>{item}</option>)}</select></label>
            <label>Assignee<input name="assignee" value={form.assignee} onChange={change} placeholder="Team member" maxLength={100} /></label>
            <label>Due date<input type="date" name="due_date" value={form.due_date} onChange={change} /></label>
          </div>
          {formError && <p className="form-error" role="alert">{formError}</p>}
          <div className="modal-actions"><button type="button" className="button button-quiet" onClick={onClose}>Cancel</button><button type="submit" className="button button-primary" disabled={saving}>{saving ? <LoaderCircle className="spin" size={16} /> : <Plus size={16} />}{saving ? 'Saving…' : 'Create task'}</button></div>
        </form>
      </section>
    </div>
  )
}

function App() {
  const [tasks, setTasks] = useState([])
  const [stats, setStats] = useState({ total: 0, todo: 0, in_progress: 0, completed: 0, overdue: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeStatus, setActiveStatus] = useState('All tasks')
  const [search, setSearch] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [saving, setSaving] = useState(false)
  const [busyTask, setBusyTask] = useState(null)
  const [notice, setNotice] = useState('')

  const load = useCallback(async () => {
    setError('')
    try {
      const [taskData, statData] = await Promise.all([api('/api/tasks'), api('/api/tasks/stats')])
      setTasks(taskData)
      setStats(statData)
    } catch (loadError) {
      setError(`${loadError.message}. Check that the backend and database are running.`)
    } finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const visibleTasks = useMemo(() => tasks.filter((task) => {
    const statusMatches = activeStatus === 'All tasks' || task.status === activeStatus
    const query = search.toLowerCase().trim()
    const searchMatches = !query || [task.title, task.description, task.assignee].filter(Boolean).some((value) => value.toLowerCase().includes(query))
    return statusMatches && searchMatches
  }), [tasks, activeStatus, search])

  const saveTask = async (payload) => {
    setSaving(true)
    try {
      await api('/api/tasks', { method: 'POST', body: JSON.stringify(payload) })
      setModalOpen(false)
      setNotice('Task created successfully.')
      await load()
    } catch (saveError) { throw saveError } finally { setSaving(false) }
  }

  const cycleStatus = async (task) => {
    const next = task.status === 'Todo' ? 'In Progress' : task.status === 'In Progress' ? 'Done' : 'Todo'
    setBusyTask(task.id)
    try {
      await api(`/api/tasks/${task.id}`, { method: 'PUT', body: JSON.stringify({ status: next }) })
      setNotice(`“${task.title}” moved to ${next}.`)
      await load()
    } catch (updateError) { setError(updateError.message) } finally { setBusyTask(null) }
  }

  const deleteTask = async (task) => {
    if (!window.confirm(`Delete “${task.title}”? This cannot be undone.`)) return
    setBusyTask(task.id)
    try {
      await api(`/api/tasks/${task.id}`, { method: 'DELETE' })
      setNotice('Task deleted.')
      await load()
    } catch (deleteError) { setError(deleteError.message) } finally { setBusyTask(null) }
  }

  useEffect(() => {
    if (!notice) return undefined
    const timeout = window.setTimeout(() => setNotice(''), 3200)
    return () => window.clearTimeout(timeout)
  }, [notice])

  const now = new Date()
  const dateLabel = new Intl.DateTimeFormat('en', { weekday: 'long', month: 'long', day: 'numeric' }).format(now)

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><Layers size={21} strokeWidth={2.4} /></div><span>taskboard<span className="brand-dot">.</span></span></div>
        <div className="workspace-switch"><div className="workspace-avatar">N</div><div className="workspace-copy"><strong>Northstar Studio</strong><span>Free workspace</span></div><ChevronDown size={15} /></div>
        <p className="nav-label">WORKSPACE</p>
        <nav className="main-nav" aria-label="Main navigation">
          <button className="nav-item"><LayoutDashboard size={17} />Overview</button>
          <button className="nav-item active"><ClipboardList size={17} />Tasks<span className="nav-count">{stats.total}</span></button>
          <button className="nav-item"><CalendarDays size={17} />Calendar</button>
          <button className="nav-item"><Activity size={17} />Activity</button>
        </nav>
        <div className="sidebar-section-head"><p className="nav-label">YOUR VIEWS</p><button className="tiny-icon" aria-label="Add view"><Plus size={15} /></button></div>
        <button className="view-item"><span className="view-dot dot-purple" />My tasks</button>
        <button className="view-item"><span className="view-dot dot-orange" />High priority</button>
        <button className="view-item"><span className="view-dot dot-green" />Completed</button>
        <div className="sidebar-bottom">
          <div className="upgrade-card"><div className="upgrade-icon"><ShieldCheck size={17} /></div><strong>Keep projects moving</strong><p>Bring tasks, people, and progress together in one place.</p><button onClick={() => setNotice('You are using the TaskBoard capstone workspace.')}>Explore workspace <ArrowRight size={13} /></button></div>
          <button className="nav-item"><Settings2 size={17} />Settings</button>
          <div className="profile-row"><div className="profile-avatar">H</div><div className="profile-copy"><strong>Harish</strong><span>Project admin</span></div><MoreHorizontal size={18} /></div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar"><div className="breadcrumbs"><span>Workspace</span><span className="crumb-slash">/</span><strong>Tasks</strong></div><div className="topbar-actions"><div className="top-date"><CalendarDays size={15} />{dateLabel}</div><button className="icon-button notification-button" aria-label="Notifications" onClick={() => setNotice('You are all caught up.')}><Bell size={17} /><span /></button><div className="top-avatar">H</div></div></header>
        <div className="page-content">
          <section className="page-heading"><div><div className="heading-kicker"><span className="green-pulse" /> PROJECT OPERATIONS</div><h1>Good work starts here.</h1><p>Keep your team aligned and make progress visible.</p></div><button className="button button-primary create-top" onClick={() => setModalOpen(true)}><Plus size={17} />New task</button></section>

          {error && <div className="alert alert-error"><span>{error}</span><button onClick={load}>Retry</button></div>}
          {notice && <div className="toast" role="status"><Check size={15} />{notice}<button aria-label="Dismiss notification" onClick={() => setNotice('')}><X size={14} /></button></div>}

          <section className="stats-grid" aria-label="Task summary">
            <article className="stat-card stat-highlight"><div className="stat-top"><span className="stat-icon icon-blue"><ListTodo size={17} /></span><span className="stat-caption">ALL TASKS</span><span className="stat-trend"><ArrowDownRight size={13} /> LIVE</span></div><div className="stat-number">{loading ? '—' : stats.total}</div><div className="stat-bottom"><span>Total tasks in your workspace</span><span className="stat-mini-line"><i /><i /><i /><i /><i /><i /><i /></span></div></article>
            <article className="stat-card"><div className="stat-top"><span className="stat-icon icon-amber"><Clock3 size={17} /></span><span className="stat-caption">IN PROGRESS</span></div><div className="stat-number">{loading ? '—' : stats.in_progress}</div><div className="stat-bottom"><span>Work currently underway</span><span className="stat-foot-dot amber-dot" /></div></article>
            <article className="stat-card"><div className="stat-top"><span className="stat-icon icon-green"><CheckCircle2 size={17} /></span><span className="stat-caption">COMPLETED</span></div><div className="stat-number">{loading ? '—' : stats.completed}</div><div className="stat-bottom"><span>Tasks across the finish line</span><span className="stat-foot-dot green-dot" /></div></article>
            <article className="stat-card"><div className="stat-top"><span className="stat-icon icon-red"><CalendarDays size={17} /></span><span className="stat-caption">OVERDUE</span></div><div className="stat-number">{loading ? '—' : stats.overdue}</div><div className="stat-bottom"><span>Tasks past their due date</span><span className="stat-foot-dot red-dot" /></div></article>
          </section>

          <section className="task-section">
            <div className="section-heading"><div><div className="section-title-line"><h2>Task overview</h2><span className="table-count">{visibleTasks.length}</span></div><p>A clear view of what needs attention next.</p></div><button className="button button-outline" onClick={load}><Activity size={15} />Refresh</button></div>
            <div className="task-toolbar"><div className="filter-tabs" role="tablist" aria-label="Filter tasks">{statuses.map((status) => <button key={status} role="tab" aria-selected={activeStatus === status} className={activeStatus === status ? 'filter-tab selected' : 'filter-tab'} onClick={() => setActiveStatus(status)}>{status}{status === 'All tasks' && <span>{stats.total}</span>}</button>)}</div><div className="toolbar-actions"><label className="search-box"><Search size={15} /><input aria-label="Search tasks" placeholder="Search tasks..." value={search} onChange={(event) => setSearch(event.target.value)} /><kbd><Command size={10} /> K</kbd></label><button className="button button-outline filter-button" onClick={() => setActiveStatus(activeStatus === 'All tasks' ? 'In Progress' : 'All tasks')}><Filter size={15} />{activeStatus === 'All tasks' ? 'Focus' : 'Clear filter'}</button></div></div>

            <div className="task-table-wrap"><table className="task-table"><thead><tr><th className="task-col">TASK</th><th>STATUS</th><th>PRIORITY</th><th>ASSIGNEE</th><th>DUE DATE</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>
              {loading ? <tr><td colSpan="6" className="table-message"><LoaderCircle className="spin" size={20} />Loading your workspace…</td></tr> : visibleTasks.length === 0 ? <tr><td colSpan="6" className="empty-state"><div className="empty-illustration"><ClipboardList size={25} /></div><strong>{error ? 'Tasks are unavailable' : 'Nothing on your plate yet'}</strong><p>{error ? 'Reconnect the backend, then try again.' : search || activeStatus !== 'All tasks' ? 'Try another search or filter.' : 'Create your first task to get the team moving.'}</p>{!error && <button className="button button-primary" onClick={() => setModalOpen(true)}><Plus size={15} />Create first task</button>}</td></tr> : visibleTasks.map((task) => (
                <tr key={task.id} className={busyTask === task.id ? 'row-busy' : ''}>
                  <td className="task-name-cell"><div className={`task-check task-check-${task.status.toLowerCase().replace(' ', '-')}`}><button title={`Move task from ${task.status} to next status`} aria-label={`Advance status for ${task.title}`} disabled={busyTask === task.id} onClick={() => cycleStatus(task)}>{task.status === 'Done' ? <Check size={13} /> : <span />}</button></div><div className="task-name-copy"><strong>{task.title}</strong>{task.description && <span>{task.description}</span>}</div></td>
                  <td><StatusBadge status={task.status} /></td><td><PriorityBadge priority={task.priority} /></td>
                  <td>{task.assignee ? <div className="assignee"><span className={`assignee-avatar avatar-${(task.assignee.charCodeAt(0) % 4)}`}>{task.assignee.slice(0, 1).toUpperCase()}</span><span>{task.assignee}</span></div> : <span className="unassigned">Unassigned</span>}</td>
                  <td>{task.due_date ? <span className={`due-date ${task.due_date < new Date().toISOString().slice(0, 10) && task.status !== 'Done' ? 'due-overdue' : ''}`}><CalendarDays size={13} />{new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric' }).format(new Date(`${task.due_date}T12:00:00`))}</span> : <span className="unassigned">—</span>}</td>
                  <td><button className="row-action" aria-label={`Delete ${task.title}`} title="Delete task" onClick={() => deleteTask(task)} disabled={busyTask === task.id}><Trash2 size={15} /></button></td>
                </tr>
              ))}
            </tbody></table></div>
            <div className="table-footer"><span>Showing <strong>{visibleTasks.length}</strong> of <strong>{tasks.length}</strong> tasks</span><span className="footer-live"><span />Synced with API</span></div>
          </section>

          <section className="bottom-grid"><article className="activity-card"><div className="bottom-card-heading"><div><h3>Latest activity</h3><p>Recent movement in your workspace</p></div><button className="text-button" onClick={load}>View all <ArrowRight size={13} /></button></div>{tasks.slice(0, 3).length ? <div className="activity-list">{tasks.slice(0, 3).map((task, index) => <div className="activity-item" key={`activity-${task.id}`}><span className={`activity-icon activity-${index}`}>{task.status === 'Done' ? <CheckCircle2 size={14} /> : <ClipboardList size={14} />}</span><div><p><strong>{task.assignee || 'A teammate'}</strong> {task.status === 'Done' ? 'completed' : 'updated'} <b>{task.title}</b></p><span>{new Date(task.updated_at || task.created_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span></div></div>)}</div> : <div className="activity-empty">Create a task to start your activity feed.</div>}</article>
            <article className="pipeline-card"><div className="bottom-card-heading"><div><h3>Delivery pipeline</h3><p>Your code-to-production flow</p></div><span className="pipeline-badge"><span /> READY TO RUN</span></div><div className="pipeline-steps"><div className="pipeline-step"><span className="pipeline-step-icon"><Command size={14} /></span><div><strong>Commit</strong><span>Git & GitHub</span></div><CheckCircle2 size={15} className="pipeline-check" /></div><div className="pipeline-connector" /><div className="pipeline-step"><span className="pipeline-step-icon"><Activity size={14} /></span><div><strong>Build & scan</strong><span>Actions + Trivy</span></div><CircleDashed size={15} className="pipeline-pending" /></div><div className="pipeline-connector" /><div className="pipeline-step"><span className="pipeline-step-icon"><Layers size={14} /></span><div><strong>Deploy</strong><span>Helm on Kubernetes</span></div><CircleDashed size={15} className="pipeline-pending" /></div></div></article>
          </section>
          <footer className="page-footer"><span>TaskBoard <span>·</span> DevOps capstone</span><span><span className="footer-status-dot" /> API-backed workspace <span className="footer-separator">·</span> v1.0.0</span></footer>
        </div>
      </main>
      {modalOpen && <TaskModal onClose={() => setModalOpen(false)} onSave={saveTask} saving={saving} />}
    </div>
  )
}

export default App
