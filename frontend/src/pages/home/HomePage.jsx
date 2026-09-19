import { useEffect, useState } from "react";
import { CreateRoomModal } from "./CreateRoomModal";
import { JoinRoomModal } from "./JoinRoomModal";
import { Button } from "../../components/ui/Button";
import { useLanguages } from "../../hooks/useLanguages";
import { ArrowRightIcon, GlobeIcon, TranslateArrowsIcon, FileTextIcon, UsersIcon } from "../../components/icons/Icon";
import "./home.css";

const PREVIEW_EXCHANGE = [
  { name: "Seyram", lang: "English", text: "Hello Daniel, how is your day going?" },
  { name: "Daniel", lang: "German", text: "Hallo Daniel, wie läuft dein Tag?", isTranslation: true },
  { name: "Daniel", lang: "German", text: "Heute ist sehr gut." },
  { name: "Seyram", lang: "English", text: "Today is very good.", isTranslation: true },
];

export function HomePage() {
  const [modal, setModal] = useState(null); // null | 'create' | 'join'
  const { languages } = useLanguages();
  const [prefillCode, setPrefillCode] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("room");
    if (code) {
      setPrefillCode(code.toUpperCase().slice(0, 4));
      setModal("join");
    }
  }, []);

  return (
    <div className="home">
      <header className="home-nav">
        <div className="home-nav-inner">
          <span className="brand">
            <TranslateArrowsIcon size={22} />
            <span>Polyglot Room</span>
          </span>
          <Button variant="ghost" size="sm" onClick={() => setModal("join")}>
            Join a room
          </Button>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-inner">
            <div className="hero-copy">
              <span className="eyebrow">Real-time multilingual chat</span>
              <h1 className="hero-title">
                One conversation. <em>Every language.</em>
              </h1>
              <p className="hero-subtitle">
                Create a room, pick your language, and talk naturally. Everyone else reads your messages in theirs,
                translated the moment you hit send.
              </p>
              <div className="hero-actions">
                <Button variant="primary" size="lg" onClick={() => setModal("create")} icon={<ArrowRightIcon size={18} />} iconPosition="right">
                  Create a room
                </Button>
                <Button variant="secondary" size="lg" onClick={() => setModal("join")}>
                  Join a room
                </Button>
              </div>
              <p className="hero-trust">No sign-up. Nothing is saved once your room closes.</p>
            </div>

            <div className="hero-preview" aria-hidden="true">
              <div className="preview-window">
                <div className="preview-window-bar">
                  <span className="preview-dot" />
                  <span className="preview-dot" />
                  <span className="preview-dot" />
                  <span className="preview-room-code">WDFB</span>
                </div>
                <div className="preview-messages">
                  {PREVIEW_EXCHANGE.map((msg, i) => (
                    <div
                      key={i}
                      className={`preview-bubble ${msg.isTranslation ? "preview-bubble--translated" : ""} ${i % 2 === 0 ? "preview-bubble--left" : "preview-bubble--right"}`}
                      style={{ animationDelay: `${i * 1.1}s` }}
                    >
                      <span className="preview-bubble-meta">
                        {msg.name} · {msg.lang}
                      </span>
                      <span className="preview-bubble-text">{msg.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="section features" aria-labelledby="features-heading">
          <h2 className="section-heading" id="features-heading">
            Built for the moment you don't share a language
          </h2>
          <div className="feature-grid">
            <article className="feature">
              <span className="feature-number">01</span>
              <UsersIcon size={22} />
              <h3>Speak your language</h3>
              <p>Everyone types in whatever language feels natural. No one has to switch to a common tongue.</p>
            </article>
            <article className="feature">
              <span className="feature-number">02</span>
              <GlobeIcon size={22} />
              <h3>Instant translation</h3>
              <p>Every message is translated on arrival, individually, into each participant's chosen language.</p>
            </article>
            <article className="feature">
              <span className="feature-number">03</span>
              <FileTextIcon size={22} />
              <h3>Share documents</h3>
              <p>Drop in a PDF and everyone gets it back translated into their own language, ready to read.</p>
            </article>
          </div>
        </section>

        <section className="section how-it-works" aria-labelledby="how-heading">
          <h2 className="section-heading" id="how-heading">
            How it works
          </h2>
          <ol className="steps">
            <li>
              <span className="step-index">1</span>
              <div>
                <h3>Create or join</h3>
                <p>Start a room and get a 4-character code, or enter one someone shared with you.</p>
              </div>
            </li>
            <li>
              <span className="step-index">2</span>
              <div>
                <h3>Pick your language</h3>
                <p>Choose the language you want to read and write in. Everyone can pick differently.</p>
              </div>
            </li>
            <li>
              <span className="step-index">3</span>
              <div>
                <h3>Chat naturally</h3>
                <p>Send messages like you normally would. No translation step, no copy-pasting into another tab.</p>
              </div>
            </li>
            <li>
              <span className="step-index">4</span>
              <div>
                <h3>Everyone reads their language</h3>
                <p>Each person sees the conversation translated into the language they chose when they joined.</p>
              </div>
            </li>
          </ol>
        </section>

        <section className="section languages-section" aria-labelledby="languages-heading">
          <h2 className="section-heading" id="languages-heading">
            Supported languages
          </h2>
          <ul className="language-pills">
            {languages.map((lang) => (
              <li key={lang.code} className="language-pill">
                {lang.name}
                {lang.nativeName && lang.nativeName !== lang.name ? <span> · {lang.nativeName}</span> : null}
              </li>
            ))}
          </ul>
        </section>

        <section className="section privacy-section" aria-labelledby="privacy-heading">
          <div className="privacy-card">
            <h2 className="section-heading" id="privacy-heading">
              Nothing is stored
            </h2>
            <p>
              Rooms, messages, and shared documents live only in memory for as long as someone is in the room. The
              moment the last person leaves, everything about that room is deleted. No database, no history, no
              accounts.
            </p>
          </div>
        </section>
      </main>

      <footer className="home-footer">
        <p>Polyglot Room, a real-time multilingual chat platform. Final-year project demonstration.</p>
      </footer>

      {modal === "create" && <CreateRoomModal languages={languages} onClose={() => setModal(null)} />}
      {modal === "join" && (
        <JoinRoomModal languages={languages} initialCode={prefillCode} onClose={() => setModal(null)} />
      )}
    </div>
  );
}
