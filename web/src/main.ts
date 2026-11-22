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

interface LessonSection {
  heading: string
  text: string
  code?: string
  language?: string
}

interface QuizQuestion {
  question: string
  options: string[]
  answer: number
  explanation: string
}

interface InterviewQuestion {
  question: string
  answer: string
  application: string
}

interface LessonContent {
  id: string
  summary: string
  sections: LessonSection[]
  key_points: string[]
  solution: string
  solution_language: string
  quiz: QuizQuestion[]
  interview: InterviewQuestion[]
}

interface CourseInterview {
  course_id: string
  course_title: string
  lessons: { lesson_id: string; lesson_title: string; module_title: string; questions: InterviewQuestion[] }[]
}

interface LessonRef {
  lesson: Lesson
  module: Module
  course: Course
}

const app = document.querySelector<HTMLDivElement>('#app')
if (!app) throw new Error('The application root element is missing.')

let courses: Course[] = []
let progress: Record<string, boolean> = {}
let selectedCourseId = 'python'
let chatMessages: ChatMessage[] = []
let isSending = false
let loadError = ''

let openLessonId: string | null = null
let lessonLoadError = ''
const lessonCache = new Map<string, LessonContent>()
const quizChoices = new Map<string, number>()
const visibleSolutions = new Set<string>()

let openInterviewCourseId: string | null = null
let interviewLoadError = ''
const interviewCache = new Map<string, CourseInterview>()
const openAnswers = new Set<string>()

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

/** Escapes text, then renders `inline code` and **bold** spans. */
const formatInline = (text: string): string =>
  escapeHtml(text)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')

const formatText = (text: string): string =>
  text
    .split(/\n{2,}/)
    .map((paragraph) => `<p>${formatInline(paragraph.trim())}</p>`)
    .join('')

const renderCode = (code: string, language: string): string => `
  <div class="code-block">
    <div class="code-label"><span>${escapeHtml(language)}</span><button type="button" class="copy-code">Copy</button></div>
    <pre><code>${escapeHtml(code)}</code></pre>
  </div>`

const lessonHref = (lessonId: string): string => `#/lesson/${encodeURIComponent(lessonId)}`
const interviewHref = (courseId: string): string => `#/interview/${encodeURIComponent(courseId)}`

/** One interview question; the model answer and practical use are revealed on click. */
const renderInterviewItem = (key: string, item: InterviewQuestion): string => `
  <details class="interview-item" data-interview-key="${escapeHtml(key)}" ${openAnswers.has(key) ? 'open' : ''}>
    <summary><span class="iq-badge">Q</span><span class="iq-text">${formatInline(item.question)}</span><span class="iq-toggle" aria-hidden="true"></span></summary>
    <div class="interview-answer">
      <p class="answer-label">Model answer</p>
      ${formatText(item.answer)}
      <div class="in-practice"><p class="answer-label">In practice</p>${formatText(item.application)}</div>
    </div>
  </details>`

const lessonRefs = (): LessonRef[] =>
  courses.flatMap((course) =>
    course.modules.flatMap((module) => module.lessons.map((lesson) => ({ lesson, module, course }))),
  )

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
          <span class="course-number">${String(index + 1).padStart(2, '0')}</span>
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
                    <h3><a href="${lessonHref(lesson.id)}">${escapeHtml(lesson.title)}</a></h3>
                    <p>${escapeHtml(lesson.practice)}</p>
                    <span class="lesson-duration">${lesson.minutes} min · tutorial, practice and quiz</span>
                    <a class="lesson-open" href="${lessonHref(lesson.id)}">${isComplete ? 'Review lesson' : 'Start lesson'} →</a>
                  </div>
                  <button class="lesson-toggle" data-lesson="${escapeHtml(lesson.id)}">${isComplete ? 'Completed' : 'Mark done'}</button>
                </article>`
            })
            .join('')}
        </section>`,
    )
    .join('')

const renderQuiz = (lessonId: string, quiz: QuizQuestion[]): string => {
  const choiceFor = (index: number): number | undefined => quizChoices.get(`${lessonId}:${index}`)
  const answered = quiz.filter((_, index) => choiceFor(index) !== undefined).length
  const correct = quiz.filter((item, index) => choiceFor(index) === item.answer).length
  const status = answered === quiz.length ? `${correct} / ${quiz.length} correct` : `${answered} / ${quiz.length} answered`

  return `
    <section class="lesson-block quiz">
      <div class="block-heading"><h3>Check your understanding</h3><span>${status}</span></div>
      ${quiz
        .map((item, index) => {
          const choice = choiceFor(index)
          const done = choice !== undefined
          const options = item.options
            .map((option, optionIndex) => {
              const state = !done ? '' : optionIndex === item.answer ? 'correct' : optionIndex === choice ? 'incorrect' : 'dimmed'
              return `<button type="button" class="quiz-option ${state}" data-quiz-question="${index}" data-quiz-option="${optionIndex}" ${done ? 'disabled' : ''}><span class="option-letter">${String.fromCharCode(65 + optionIndex)}</span><span>${formatInline(option)}</span></button>`
            })
            .join('')
          const feedback = done
            ? `<p class="quiz-feedback ${choice === item.answer ? 'correct' : 'incorrect'}"><strong>${choice === item.answer ? 'Correct.' : 'Not quite.'}</strong> ${formatInline(item.explanation)}</p>`
            : ''
          return `
            <div class="quiz-question">
              <p class="quiz-prompt"><span>Q${index + 1}</span>${formatInline(item.question)}</p>
              <div class="quiz-options" role="group" aria-label="Answers for question ${index + 1}">${options}</div>
              ${feedback}
            </div>`
        })
        .join('')}
      ${answered ? '<button type="button" class="text-button" data-quiz-reset>Try the quiz again</button>' : ''}
    </section>`
}

const renderLessonBody = (ref: LessonRef): string => {
  const content = lessonCache.get(ref.lesson.id)
  if (!content) {
    return lessonLoadError
      ? `<p class="lesson-status error">${escapeHtml(lessonLoadError)}</p>`
      : '<p class="lesson-status">Loading lesson…</p>'
  }
  const solutionShown = visibleSolutions.has(ref.lesson.id)
  return `
    <p class="lesson-summary">${formatInline(content.summary)}</p>
    ${content.sections
      .map(
        (section) => `
          <section class="lesson-block">
            <h3>${escapeHtml(section.heading)}</h3>
            ${formatText(section.text)}
            ${section.code ? renderCode(section.code, section.language ?? 'python') : ''}
          </section>`,
      )
      .join('')}
    <section class="lesson-block key-points">
      <h3>Key points</h3>
      <ul>${content.key_points.map((point) => `<li>${formatInline(point)}</li>`).join('')}</ul>
    </section>
    <section class="lesson-block practice">
      <h3>Practice</h3>
      <p>${formatInline(ref.lesson.practice)}</p>
      <p class="practice-tip">Try it yourself first, then compare with a worked solution.</p>
      <button type="button" class="secondary-button" data-solution-toggle>${solutionShown ? 'Hide solution' : 'Show a solution'}</button>
      ${solutionShown ? renderCode(content.solution, content.solution_language) : ''}
    </section>
    ${renderQuiz(ref.lesson.id, content.quiz)}
    <section class="lesson-block interview">
      <div class="block-heading"><h3>Interview questions</h3><a href="${interviewHref(ref.course.id)}">All ${escapeHtml(ref.course.title)} questions →</a></div>
      <p class="interview-intro">Answer out loud first, then open each question to compare with a model answer and see where it's used in practice.</p>
      ${content.interview.map((item, index) => renderInterviewItem(`${ref.lesson.id}:${index}`, item)).join('')}
    </section>`
}

const renderLessonView = (ref: LessonRef): string => {
  const refs = lessonRefs()
  const index = refs.findIndex((item) => item.lesson.id === ref.lesson.id)
  const previous = refs[index - 1]
  const next = refs[index + 1]
  const isComplete = progress[ref.lesson.id] === true
  const moduleNumber = ref.course.modules.indexOf(ref.module) + 1

  return `
    <article class="lesson-view">
      <a class="back-link" href="#">← ${escapeHtml(ref.course.title)}</a>
      <p class="eyebrow">MODULE ${moduleNumber} · ${escapeHtml(ref.module.title.toUpperCase())} · ${ref.lesson.minutes} MIN</p>
      <h2 class="lesson-title">${escapeHtml(ref.lesson.title)}</h2>
      ${renderLessonBody(ref)}
      <footer class="lesson-footer">
        <button type="button" class="primary-button lesson-done ${isComplete ? 'is-complete' : ''}" data-lesson="${escapeHtml(ref.lesson.id)}">${isComplete ? '✓ Completed' : 'Mark lesson done'}</button>
        <nav class="lesson-nav" aria-label="Lesson navigation">
          ${previous ? `<a href="${lessonHref(previous.lesson.id)}">← Previous</a>` : ''}
          ${next ? `<a href="${lessonHref(next.lesson.id)}">Next: ${escapeHtml(next.lesson.title)} →</a>` : ''}
        </nav>
      </footer>
    </article>`
}

const renderInterviewPage = (course: Course): string => {
  const data = interviewCache.get(course.id)
  let body: string
  if (!data) {
    body = interviewLoadError
      ? `<p class="lesson-status error">${escapeHtml(interviewLoadError)}</p>`
      : '<p class="lesson-status">Loading interview questions…</p>'
  } else {
    const modules: string[] = []
    let currentModule = ''
    let moduleItems = ''
    const flush = (): void => {
      if (currentModule) modules.push(`<section class="lesson-block interview-module"><p class="eyebrow">${escapeHtml(currentModule.toUpperCase())}</p>${moduleItems}</section>`)
    }
    for (const lesson of data.lessons) {
      if (lesson.module_title !== currentModule) {
        flush()
        currentModule = lesson.module_title
        moduleItems = ''
      }
      moduleItems += `
        <div class="interview-lesson">
          <h3><a href="${lessonHref(lesson.lesson_id)}">${escapeHtml(lesson.lesson_title)}</a></h3>
          ${lesson.questions.map((item, index) => renderInterviewItem(`${lesson.lesson_id}:${index}`, item)).join('')}
        </div>`
    }
    flush()
    body = modules.join('')
  }
  const total = data ? data.lessons.reduce((sum, lesson) => sum + lesson.questions.length, 0) : 0

  return `
    <article class="lesson-view interview-page">
      <a class="back-link" href="#">← ${escapeHtml(course.title)}</a>
      <p class="eyebrow">INTERVIEW PREP${total ? ` · ${total} QUESTIONS` : ''}</p>
      <h2 class="lesson-title">${escapeHtml(course.title)}</h2>
      <p class="lesson-summary">Practise explaining each answer out loud, then open the question to compare with a model answer and see where the idea is used in real systems.</p>
      <div class="interview-toolbar">
        <button type="button" class="secondary-button" data-answers="show">Show all answers</button>
        <button type="button" class="secondary-button" data-answers="hide">Hide all answers</button>
      </div>
      ${body}
    </article>`
}

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

const renderWelcome = (): string => {
  const total = overallProgress()
  const percentage = total.total ? Math.round((total.done / total.total) * 100) : 0
  return `
    <section class="welcome">
      <div class="welcome-copy">
        <p class="eyebrow">LEARN BY BUILDING</p>
        <h1>Small steps.<br><span>Real projects.</span></h1>
        <p class="welcome-text">A practical path from your first Python script to algorithms, backends, databases, system design, and AI-powered apps. Learn one concept, then put it to work.</p>
        <button class="primary-button" id="continue-learning">Continue learning <span aria-hidden="true">→</span></button>
      </div>
      <div class="progress-card">
        <div class="progress-card-heading"><span>YOUR JOURNEY</span><span>${total.done} / ${total.total} lessons</span></div>
        <div class="progress-ring" style="--progress:${percentage}%"><div><strong>${percentage}%</strong><span>complete</span></div></div>
        <p>${total.done === 0 ? 'Your first step is waiting.' : `${total.total - total.done} lessons left on your roadmap.`}</p>
        <div class="progress-foot"><span>Progress saves automatically</span><span class="save-indicator">●</span></div>
      </div>
    </section>`
}

const renderRoadmap = (): string => `
  <aside class="roadmap">
    <div class="section-heading"><div><p class="eyebrow">THE ROADMAP</p><h2>Your courses</h2></div><span class="course-count">${courses.length} COURSES</span></div>
    <div class="course-list">${renderCourseList()}</div>
    <div class="roadmap-note"><span class="note-icon">i</span><p>Go at your own pace. Every lesson has a tutorial, a hands-on exercise with a solution, and a short quiz.</p></div>
  </aside>`

const renderCourse = (course: Course): string => {
  const courseTotal = courseProgress(course)
  return `
    <div class="course-heading">
      <div><p class="eyebrow">${escapeHtml(course.level.toUpperCase())} · ${courseTotal.done}/${courseTotal.total} COMPLETE</p><h2>${escapeHtml(course.title)}</h2><p class="course-subtitle">${escapeHtml(course.subtitle)}</p><a class="interview-link" href="${interviewHref(course.id)}">Interview prep: questions and answers →</a></div>
      <div class="course-progress-label">${courseTotal.total ? Math.round((courseTotal.done / courseTotal.total) * 100) : 0}%<span>complete</span></div>
    </div>
    ${renderLessons(course)}`
}

const renderCoach = (openRef: LessonRef | undefined): string => `
  <aside class="coach-panel">
    <div class="coach-heading"><span class="coach-avatar">✳</span><div><h2>Learning coach</h2><p>Ask a question, get a hint</p></div><span class="coach-online" title="Ready"></span></div>
    <div class="coach-notice"><strong>${openRef ? `Ask about “${escapeHtml(openRef.lesson.title)}”` : 'Thoughtful, step-by-step help'}</strong><p>${openRef ? 'The coach knows which lesson you are reading.' : 'The coach can explain concepts and give hints.'} It cannot change your progress or run code.</p></div>
    <div class="chat-messages" id="chat-messages">
      ${chatMessages.length ? renderChatMessages() : '<div class="chat-empty"><span>✳</span><p>What are you working on?</p><small>Ask about a lesson, concept, or error.</small></div>'}
      ${isSending ? '<div class="chat-loading"><span></span><span></span><span></span> Thinking…</div>' : ''}
    </div>
    <form class="chat-form" id="chat-form">
      <label class="sr-only" for="chat-input">Ask your learning coach</label>
      <textarea id="chat-input" name="message" rows="2" maxlength="4000" placeholder="Ask a question…" required></textarea>
      <div class="chat-form-footer"><span>Your provider key stays on the API server.</span><button type="submit" aria-label="Send message" ${isSending ? 'disabled' : ''}>↑</button></div>
    </form>
    <p class="chat-footnote">Powered by Claude when <code>ANTHROPIC_API_KEY</code> is set on the server.</p>
  </aside>`

const render = (): void => {
  const selectedCourse = courses.find((course) => course.id === selectedCourseId)
  if (!selectedCourse) {
    app.innerHTML = `<main class="loading">${loadError ? escapeHtml(loadError) : 'Loading your learning path…'}</main>`
    return
  }

  const draft = document.querySelector<HTMLTextAreaElement>('#chat-input')?.value ?? ''
  const openRef = openLessonId ? lessonRefs().find((ref) => ref.lesson.id === openLessonId) : undefined
  const interviewCourse = openInterviewCourseId ? courses.find((course) => course.id === openInterviewCourseId) : undefined
  const reading = Boolean(openRef || interviewCourse)
  const mainContent = openRef
    ? renderLessonView(openRef)
    : interviewCourse
      ? renderInterviewPage(interviewCourse)
      : renderCourse(selectedCourse)

  app.innerHTML = `
    <div class="layout">
      <header class="topbar">
        <a class="brand" href="#" aria-label="Build and Learn home"><span class="brand-mark">B</span><span>build<span class="brand-light">/learn</span></span></a>
        <div class="topbar-note"><span class="status-dot"></span> Your personal coding roadmap</div>
        <a class="docs-link" href="/docs" target="_blank" rel="noreferrer">Explore the API <span aria-hidden="true">↗</span></a>
      </header>

      <main>
        ${reading ? '' : renderWelcome()}
        <div class="workspace ${reading ? 'reading' : ''}">
          ${reading ? '' : renderRoadmap()}
          <section class="course-content">${mainContent}</section>
          ${renderCoach(openRef)}
        </div>
      </main>
      <footer class="footer"><span>Made for curious minds.</span><span>Learn it. Build it. Keep going.</span></footer>
    </div>`

  attachHandlers()
  const input = document.querySelector<HTMLTextAreaElement>('#chat-input')
  if (input && draft) input.value = draft
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
    const refs = lessonRefs()
    const next =
      refs.find((ref) => ref.course.id === selectedCourseId && !progress[ref.lesson.id]) ??
      refs.find((ref) => !progress[ref.lesson.id])
    if (next) window.location.hash = lessonHref(next.lesson.id)
  })

  document.querySelectorAll<HTMLButtonElement>('[data-quiz-option]').forEach((button) => {
    button.addEventListener('click', () => {
      if (!openLessonId) return
      quizChoices.set(`${openLessonId}:${button.dataset.quizQuestion}`, Number(button.dataset.quizOption))
      render()
    })
  })

  document.querySelector<HTMLButtonElement>('[data-quiz-reset]')?.addEventListener('click', () => {
    if (!openLessonId) return
    for (const key of [...quizChoices.keys()]) {
      if (key.startsWith(`${openLessonId}:`)) quizChoices.delete(key)
    }
    render()
  })

  document.querySelector<HTMLButtonElement>('[data-solution-toggle]')?.addEventListener('click', () => {
    if (!openLessonId) return
    if (visibleSolutions.has(openLessonId)) visibleSolutions.delete(openLessonId)
    else visibleSolutions.add(openLessonId)
    render()
  })

  document.querySelectorAll<HTMLDetailsElement>('[data-interview-key]').forEach((item) => {
    item.addEventListener('toggle', () => {
      const key = item.dataset.interviewKey ?? ''
      if (item.open) openAnswers.add(key)
      else openAnswers.delete(key)
    })
  })

  document.querySelectorAll<HTMLButtonElement>('[data-answers]').forEach((button) => {
    button.addEventListener('click', () => {
      const show = button.dataset.answers === 'show'
      document.querySelectorAll<HTMLDetailsElement>('[data-interview-key]').forEach((item) => {
        const key = item.dataset.interviewKey ?? ''
        if (show) openAnswers.add(key)
        else openAnswers.delete(key)
      })
      render()
    })
  })

  document.querySelectorAll<HTMLButtonElement>('.copy-code').forEach((button) => {
    button.addEventListener('click', () => {
      const code = button.closest('.code-block')?.querySelector('code')?.textContent ?? ''
      navigator.clipboard.writeText(code).then(
        () => { button.textContent = 'Copied' },
        () => { button.textContent = 'Copy failed' },
      )
    })
  })

  document.querySelector<HTMLFormElement>('#chat-form')?.addEventListener('submit', (event) => {
    event.preventDefault()
    const input = document.querySelector<HTMLTextAreaElement>('#chat-input')
    const content = input?.value.trim()
    if (input && content && !isSending) {
      input.value = ''
      void sendMessage(content)
    }
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
      body: JSON.stringify({ messages: chatMessages.slice(-12), lesson_id: openLessonId }),
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

const loadLesson = async (lessonId: string): Promise<void> => {
  if (lessonCache.has(lessonId)) return
  lessonLoadError = ''
  try {
    const response = await fetch(`/api/lessons/${encodeURIComponent(lessonId)}`)
    if (!response.ok) throw new Error(`Could not load this lesson (${response.status}).`)
    lessonCache.set(lessonId, (await response.json()) as LessonContent)
  } catch (error) {
    lessonLoadError = error instanceof Error ? error.message : 'Could not load this lesson.'
  }
  if (openLessonId === lessonId) render()
}

const loadInterview = async (courseId: string): Promise<void> => {
  if (interviewCache.has(courseId)) return
  interviewLoadError = ''
  try {
    const response = await fetch(`/api/courses/${encodeURIComponent(courseId)}/interview`)
    if (!response.ok) throw new Error(`Could not load the interview questions (${response.status}).`)
    interviewCache.set(courseId, (await response.json()) as CourseInterview)
  } catch (error) {
    interviewLoadError = error instanceof Error ? error.message : 'Could not load the interview questions.'
  }
  if (openInterviewCourseId === courseId) render()
}

const routeFromHash = (): { kind: 'lesson' | 'interview'; id: string } | null => {
  const match = /^#\/(lesson|interview)\/([^/]+)$/.exec(window.location.hash)
  return match ? { kind: match[1] as 'lesson' | 'interview', id: decodeURIComponent(match[2]) } : null
}

/** Shows the lesson or interview page named in the URL hash, or the course overview. */
const showRoute = (): void => {
  const previousLessonId = openLessonId
  const route = routeFromHash()
  const ref = route?.kind === 'lesson' ? lessonRefs().find((item) => item.lesson.id === route.id) : undefined
  const interviewCourse = route?.kind === 'interview' ? courses.find((course) => course.id === route.id) : undefined
  openLessonId = ref ? ref.lesson.id : null
  openInterviewCourseId = interviewCourse ? interviewCourse.id : null
  lessonLoadError = ''
  interviewLoadError = ''
  if (ref) selectedCourseId = ref.course.id
  if (interviewCourse) selectedCourseId = interviewCourse.id
  render()
  if (ref) {
    window.scrollTo({ top: 0 })
    void loadLesson(ref.lesson.id)
  } else if (interviewCourse) {
    window.scrollTo({ top: 0 })
    void loadInterview(interviewCourse.id)
  } else if (previousLessonId) {
    document.querySelector(`[data-lesson="${CSS.escape(previousLessonId)}"]`)?.scrollIntoView({ block: 'center' })
  }
}

window.addEventListener('hashchange', showRoute)

const load = async (): Promise<void> => {
  try {
    const [courseResponse, progressResponse] = await Promise.all([
      fetch('/api/courses'),
      fetch('/api/progress'),
    ])
    if (!courseResponse.ok || !progressResponse.ok) throw new Error('The learning API is unavailable. Start the FastAPI server and refresh.')
    courses = (await courseResponse.json()) as Course[]
    progress = (await progressResponse.json()) as Record<string, boolean>
    showRoute()
  } catch (error) {
    loadError = error instanceof Error ? error.message : 'Could not load the learning path.'
    render()
  }
}

void load()
