import './style.css'

interface Lesson {
  id: string
  title: string
  practice: string
  minutes: number
}

interface Module {
  title: string
  lessons: Lesson[]
}

interface Course {
  id: string
  title: string
  subtitle: string
  level: string
  modules: Module[]
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

const app = document.querySelector<HTMLDivElement>('#app')
if (!app) throw new Error('The application root element is missing.')

let courses: Course[] = []
let progress: Record<string, boolean> = {}
let selectedCourseId = 'python'
let chatMessages: ChatMessage[] = []
let isSending = false
let loadError = ''

const escapeHtml = (value: string): string =>
  value.replace(/[&<>"']/g, (character) => {
    const entities: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    }
    return entities[character] ?? character
  })

const allLessons = (): Lesson[] =>
  courses.flatMap((course) => course.modules.flatMap((module) => module.lessons))

const courseProgress = (course: Course): { done: number; total: number } => {
  const lessons = course.modules.flatMap((module) => module.lessons)
  return {
    done: lessons.filter((lesson) => progress[lesson.id]).length,
    total: lessons.length,
  }
}

const overallProgress = (): { done: number; total: number } => {
  const lessons = allLessons()
  return {
    done: lessons.filter((lesson) => progress[lesson.id]).length,
    total: lessons.length,
  }
}

const renderCourseList = (): string =>
  courses
    .map((course, index) => {
      const { done, total } = courseProgress(course)
      const percentage = total ? Math.round((done / total) * 100) : 0
      return `
        <button class="course-card ${course.id === selectedCourseId ? 'selected' : ''}" data-course="${escapeHtml(course.id)}">
          <span class="course-number">0${index + 1}</span>
          <span class="course-card-copy">
            <span class="course-name">${escapeHtml(course.title)}</span>
            <span class="course-meta">${done} of ${total} lessons · ${escapeHtml(course.level)}</span>
            <span class="mini-track"><span style="width:${percentage}%"></span></span>
          </span>
          <span class="course-arrow" aria-hidden="true">→</span>
        </button>`
    })
    .join('')

const renderLessons = (course: Course): string =>
  course.modules
    .map(
      (module, index) => `
        <section class="module">
          <div class="module-title"><span class="module-number">${String(index + 1).padStart(2, '0')}</span>${escapeHtml(module.title)}</div>
          ${module.lessons
            .map((lesson) => {
              const isComplete = progress[lesson.id] === true
              return `
                <article class="lesson ${isComplete ? 'completed' : ''}">
                  <button class="lesson-check" data-lesson="${escapeHtml(lesson.id)}" aria-label="${isComplete ? 'Mark incomplete' : 'Mark complete'}: ${escapeHtml(lesson.title)}">${isComplete ? '✓' : ''}</button>
                  <div class="lesson-copy">
                    <h3>${escapeHtml(lesson.title)}</h3>
                    <p>${escapeHtml(lesson.practice)}</p>
                    <span class="lesson-duration">${lesson.minutes} min · hands-on</span>
                  </div>
                  <button class="lesson-toggle" data-lesson="${escapeHtml(lesson.id)}">${isComplete ? 'Completed' : 'Mark done'}</button>
                </article>`
            })
            .join('')}
        </section>`,
    )
    .join('')

const renderChatMessages = (): string =>
  chatMessages
    .map(
      (message) => `
        <div class="chat-message ${message.role}">
          <span class="chat-role">${message.role === 'user' ? 'You' : 'Learning coach'}</span>
          <p>${escapeHtml(message.content).replace(/\n/g, '<br>')}</p>
        </div>`,
    )
    .join('')

const render = (): void => {
  const selectedCourse = courses.find((course) => course.id === selectedCourseId)
  if (!selectedCourse) {
    app.innerHTML = `<main class="loading">${loadError ? escapeHtml(loadError) : 'Loading your learning path…'}</main>`
    return
  }

  const total = overallProgress()
  const percentage = total.total ? Math.round((total.done / total.total) * 100) : 0
  const courseTotal = courseProgress(selectedCourse)

  app.innerHTML = `
    <div class="layout">
      <header class="topbar">
        <a class="brand" href="#" aria-label="Build and Learn home"><span class="brand-mark">B</span><span>build<span class="brand-light">/learn</span></span></a>
        <div class="topbar-note"><span class="status-dot"></span> Your personal coding roadmap</div>
        <a class="docs-link" href="/docs" target="_blank" rel="noreferrer">Explore the API <span aria-hidden="true">↗</span></a>
      </header>

      <main>
        <section class="welcome">
          <div class="welcome-copy">
            <p class="eyebrow">LEARN BY BUILDING</p>
            <h1>Small steps.<br><span>Real projects.</span></h1>
            <p class="welcome-text">A practical path from your first Python script to AI-powered apps. Learn one concept, then put it to work.</p>
            <button class="primary-button" id="continue-learning">Continue learning <span aria-hidden="true">→</span></button>
          </div>
          <div class="progress-card">
            <div class="progress-card-heading"><span>YOUR JOURNEY</span><span>${total.done} / ${total.total} lessons</span></div>
            <div class="progress-ring" style="--progress:${percentage}%"><div><strong>${percentage}%</strong><span>complete</span></div></div>
            <p>${total.done === 0 ? 'Your first step is waiting.' : `${total.total - total.done} lessons left on your roadmap.`}</p>
            <div class="progress-foot"><span>Progress saves automatically</span><span class="save-indicator">●</span></div>
          </div>
        </section>

        <div class="workspace">
          <aside class="roadmap">
            <div class="section-heading"><div><p class="eyebrow">THE ROADMAP</p><h2>Five courses</h2></div><span class="course-count">${courses.length} COURSES</span></div>
            <div class="course-list">${renderCourseList()}</div>
            <div class="roadmap-note"><span class="note-icon">i</span><p>Go at your own pace. Every lesson includes a small project to help the ideas stick.</p></div>
          </aside>

          <section class="course-content">
            <div class="course-heading">
              <div><p class="eyebrow">${escapeHtml(selectedCourse.level.toUpperCase())} · ${courseTotal.done}/${courseTotal.total} COMPLETE</p><h2>${escapeHtml(selectedCourse.title)}</h2><p class="course-subtitle">${escapeHtml(selectedCourse.subtitle)}</p></div>
              <div class="course-progress-label">${courseTotal.total ? Math.round((courseTotal.done / courseTotal.total) * 100) : 0}%<span>complete</span></div>
            </div>
            ${renderLessons(selectedCourse)}
          </section>

          <aside class="coach-panel">
            <div class="coach-heading"><span class="coach-avatar">✳</span><div><h2>Learning coach</h2><p>Ask a question, get a hint</p></div><span class="coach-online" title="Ready"></span></div>
            <div class="coach-notice"><strong>Thoughtful, step-by-step help</strong><p>The coach can explain concepts and give hints. It cannot change your progress or run code.</p></div>
            <div class="chat-messages" id="chat-messages">
              ${chatMessages.length ? renderChatMessages() : '<div class="chat-empty"><span>✳</span><p>What are you working on?</p><small>Ask about a lesson, concept, or error.</small></div>'}
              ${isSending ? '<div class="chat-loading"><span></span><span></span><span></span> Thinking…</div>' : ''}
            </div>
            <form class="chat-form" id="chat-form">
              <label class="sr-only" for="chat-input">Ask your learning coach</label>
              <textarea id="chat-input" name="message" rows="2" maxlength="4000" placeholder="Ask a question…" required></textarea>
              <div class="chat-form-footer"><span>Your provider key stays on the API server.</span><button type="submit" aria-label="Send message" ${isSending ? 'disabled' : ''}>↑</button></div>
            </form>
            <p class="chat-footnote">Configure an OpenAI-compatible provider in <code>api/.env</code>.</p>
          </aside>
        </div>
      </main>
      <footer class="footer"><span>Made for curious minds.</span><span>Learn it. Build it. Keep going.</span></footer>
    </div>`

  attachHandlers()
  const messages = document.querySelector<HTMLDivElement>('#chat-messages')
  if (messages) messages.scrollTop = messages.scrollHeight
}

const attachHandlers = (): void => {
  document.querySelectorAll<HTMLButtonElement>('[data-course]').forEach((button) => {
    button.addEventListener('click', () => {
      selectedCourseId = button.dataset.course ?? selectedCourseId
      render()
    })
  })

  document.querySelectorAll<HTMLButtonElement>('[data-lesson]').forEach((button) => {
    button.addEventListener('click', () => {
      const lessonId = button.dataset.lesson
      if (lessonId) void updateProgress(lessonId, !progress[lessonId])
    })
  })

  document.querySelector<HTMLButtonElement>('#continue-learning')?.addEventListener('click', () => {
    const course = courses.find((item) => item.id === selectedCourseId)
    const nextLesson = course?.modules.flatMap((module) => module.lessons).find((lesson) => !progress[lesson.id])
    if (nextLesson) {
      document.querySelector(`[data-lesson="${CSS.escape(nextLesson.id)}"]`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    } else {
      const nextCourse = courses.find((item) => courseProgress(item).done < courseProgress(item).total)
      if (nextCourse) {
        selectedCourseId = nextCourse.id
        render()
      }
    }
  })

  document.querySelector<HTMLFormElement>('#chat-form')?.addEventListener('submit', (event) => {
    event.preventDefault()
    const input = document.querySelector<HTMLTextAreaElement>('#chat-input')
    const content = input?.value.trim()
    if (content && !isSending) void sendMessage(content)
  })
}

const updateProgress = async (lessonId: string, completed: boolean): Promise<void> => {
  const button = document.querySelector<HTMLButtonElement>(`[data-lesson="${CSS.escape(lessonId)}"]`)
  if (button) button.disabled = true
  try {
    const response = await fetch(`/api/progress/${encodeURIComponent(lessonId)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed }),
    })
    if (!response.ok) throw new Error(`Could not save your progress (${response.status}).`)
    progress[lessonId] = completed
    render()
  } catch (error) {
    window.alert(error instanceof Error ? error.message : 'Could not save your progress.')
    if (button) button.disabled = false
  }
}

const sendMessage = async (content: string): Promise<void> => {
  chatMessages.push({ role: 'user', content })
  isSending = true
  render()

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: chatMessages.slice(-12) }),
    })
    const payload: { reply?: string; detail?: string } = await response.json()
    if (!response.ok) throw new Error(payload.detail ?? `The coach request failed (${response.status}).`)
    if (!payload.reply) throw new Error('The coach returned an empty reply.')
    chatMessages.push({ role: 'assistant', content: payload.reply })
  } catch (error) {
    chatMessages.pop()
    window.alert(error instanceof Error ? error.message : 'Could not reach the learning coach.')
  } finally {
    isSending = false
    render()
  }
}

const load = async (): Promise<void> => {
  try {
    const [courseResponse, progressResponse] = await Promise.all([
      fetch('/api/courses'),
      fetch('/api/progress'),
    ])
    if (!courseResponse.ok || !progressResponse.ok) throw new Error('The learning API is unavailable. Start the FastAPI server and refresh.')
    courses = (await courseResponse.json()) as Course[]
    progress = (await progressResponse.json()) as Record<string, boolean>
    render()
  } catch (error) {
    loadError = error instanceof Error ? error.message : 'Could not load the learning path.'
    render()
  }
}

void load()
