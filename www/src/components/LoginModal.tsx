"use client";

import {
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
  type CSSProperties,
  type FormEvent,
  type ReactElement,
} from "react";
import { createPortal } from "react-dom";

export type AuthModalVariant = "login" | "signup";

type LoginModalProps = {
  open: boolean;
  variant: AuthModalVariant;
  onClose: () => void;
  onSuccess: (email: string) => void;
};

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const USER_ID_RE = /^[a-zA-Z0-9_]{2,64}$/;
const PHONE_RE = /^01[0-9][0-9]{7,8}$/;
const MIN_PASSWORD = 6;

function normalizePhone(raw: string): string {
  return raw.replace(/\D/g, "");
}

/** 회원가입 API — dev 는 next.config.ts rewrites 가 /signup → backend (기본 포트 8000) 로 프록시. */
function getApiBase(): string {
  const base = process.env.NEXT_PUBLIC_API_BASE?.trim();
  if (base) return base.replace(/\/$/, "");
  return "";
}

function getSignupUrl(): string {
  const base = getApiBase();
  if (base) {
    if (base.endsWith("/signup")) return base;
    return `${base}/signup`;
  }
  return "/signup";
}

/** 구글 로그인 시작 URL — backend가 구글 인증 후 현재 origin으로 되돌려 보낸다. */
function getGoogleLoginUrl(): string {
  const base = getApiBase();
  const returnTo = encodeURIComponent(window.location.origin);
  return `${base}/auth/google/login?return_to=${returnTo}`;
}

function GoogleLogo() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden className="flex-shrink-0">
      <path
        fill="#4285F4"
        d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z"
      />
      <path
        fill="#34A853"
        d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z"
      />
      <path
        fill="#FBBC05"
        d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z"
      />
      <path
        fill="#EA4335"
        d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"
      />
    </svg>
  );
}

type SocialProvider = {
  id: string;
  label: string;
  style: CSSProperties;
  enabled: boolean;
  icon?: () => ReactElement;
};

// 전역 CSS(globals.css `button { color: inherit }`)가 레이어 밖 규칙이라 Tailwind
// text-color 유틸리티(레이어 안)보다 항상 우선한다 — 색은 className이 아니라
// style로 강제해야 실제로 반영된다.
const SOCIAL_PROVIDERS: SocialProvider[] = [
  {
    id: "google",
    label: "구글로 로그인",
    style: { backgroundColor: "#ffffff", color: "#1f1f1f", border: "1px solid rgba(0,0,0,0.15)" },
    enabled: true,
    icon: GoogleLogo,
  },
  {
    id: "naver",
    label: "네이버 아이디로 로그인",
    style: { backgroundColor: "#03c75a", color: "#ffffff", border: "none" },
    enabled: false,
  },
  {
    id: "kakao",
    label: "카카오계정으로 로그인",
    style: { backgroundColor: "#fee500", color: "#191600", border: "none" },
    enabled: false,
  },
  {
    id: "apple",
    label: "Apple로 로그인",
    style: { backgroundColor: "#000000", color: "#ffffff", border: "none" },
    enabled: false,
  },
  {
    id: "instagram",
    label: "Instagram으로 로그인",
    style: {
      background: "linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888)",
      color: "#ffffff",
      border: "none",
    },
    enabled: false,
  },
];

function sleep(ms: number): Promise<void> {
  return new Promise((r) => window.setTimeout(r, ms));
}

async function ensureApiReachable(): Promise<string | null> {
  const pingUrl = getApiBase() ? `${getApiBase()}/ping` : "/ping";
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const res = await fetch(pingUrl, { method: "GET" });
      if (res.ok) return null;
      if (res.status >= 500 && attempt === 0) {
        await sleep(400);
        continue;
      }
      return `API 응답 오류 (${res.status}). backend\\apps 에서 python main.py 상태를 확인하세요.`;
    } catch {
      if (attempt === 0) {
        await sleep(400);
        continue;
      }
      return (
        "백엔드 API(8000)에 연결할 수 없습니다.\n" +
        "1) backend\\apps 에서 python main.py 실행\n" +
        "2) 터미널에 'Application startup complete' 확인\n" +
        "3) frontend 에서 npm run dev 실행 후 다시 시도\n" +
        "4) Windows 에서 UVICORN_RELOAD=1 이면 저장할 때마다 API 가 잠깐 끊길 수 있음"
      );
    }
  }
  return null;
}

function logSignupPayload(phase: string, values: Record<string, unknown>): void {
  console.log(`[회원가입] ${phase}`, values);
}

/** 콘솔 로그용 — 비밀번호 필드 마스킹 */
function redactSignupForLog(
  body: Record<string, unknown>,
): Record<string, unknown> {
  const out = { ...body };
  if ("password" in out) out.password = "[redacted]";
  if ("password_confirm" in out) out.password_confirm = "[redacted]";
  return out;
}

function parseHttpError(status: number, raw: string): string {
  if (!raw.trim()) {
    if (status === 409) return "이미 사용 중인 아이디 또는 이메일입니다.";
    if (status === 400) return "입력값이 올바르지 않거나 중복된 정보입니다.";
    if (status === 422) return "입력 형식이 올바르지 않습니다.";
    if (status === 503) return "데이터베이스에 연결할 수 없습니다. API 서버를 확인하세요.";
    if (status === 404) {
      return "회원가입 API를 찾을 수 없습니다. backend/apps 에서 python main.py 를 실행하세요.";
    }
    if (status === 502 || status === 503) {
      return (
        "백엔드 API가 꺼져 있거나 재시작 중입니다 (502).\n" +
        "backend\\apps 에서 python main.py 를 다시 실행하고 " +
        "'Application startup complete' 가 보인 뒤 회원가입하세요."
      );
    }
    return `서버 오류 (${status}). API(8000)가 실행 중인지 확인하세요.`;
  }
  try {
    const j = JSON.parse(raw) as { detail?: unknown; message?: string };
    const d = j.detail ?? j.message;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) {
      const parts = d
        .map((x) => {
          if (typeof x === "object" && x !== null && "msg" in x) {
            return String((x as { msg?: string }).msg ?? "");
          }
          return typeof x === "string" ? x : "";
        })
        .filter(Boolean);
      if (parts.length) return parts.join(", ");
    }
  } catch {
    /* ignore */
  }
  return raw.trim().slice(0, 300);
}

type LoginModalFormState = {
  userId: string;
  email: string;
  nickname: string;
  phone: string;
  password: string;
  passwordConfirm: string;
  error: string | null;
  submitting: boolean;
};

function createInitialFormState(): LoginModalFormState {
  return {
    userId: "",
    email: "",
    nickname: "",
    phone: "",
    password: "",
    passwordConfirm: "",
    error: null,
    submitting: false,
  };
}

/** FormData → 문자열 맵 (체크박스 등 File 제외 시) */
function formDataToStringRecord(fd: FormData): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [k, v] of fd.entries()) {
    if (typeof v === "string") out[k] = v;
  }
  return out;
}

const FIELD = "mb-4";
const LABEL =
  "block mb-[6px] text-xs font-bold tracking-[0.04em] uppercase text-[rgba(148,163,184,0.95)]";
const INPUT =
  "w-full p-[12px_14px] rounded-[10px] border border-[rgba(148,163,184,0.25)] bg-[rgba(4,7,15,0.75)] text-white text-[15px] transition placeholder:text-[rgba(100,116,139,0.9)] focus:outline-none focus:border-[#00e5ff] focus:shadow-[0_0_0_2px_rgba(0,229,255,0.2)]";

export default function LoginModal({
  open,
  variant,
  onClose,
  onSuccess,
}: LoginModalProps) {
  const titleId = useId();
  const userIdRef = useRef<HTMLInputElement>(null);
  const emailRef = useRef<HTMLInputElement>(null);
  const [state, setState] = useState<LoginModalFormState>(createInitialFormState);

  const patch = useCallback((p: Partial<LoginModalFormState>) => {
    setState((prev) => ({ ...prev, ...p }));
  }, []);

  const handleSocialClick = useCallback(
    (provider: SocialProvider) => {
      if (provider.id === "google") {
        window.location.href = getGoogleLoginUrl();
        return;
      }
      patch({ error: "준비 중인 로그인 방식입니다." });
    },
    [patch],
  );

  useEffect(() => {
    if (!open) return;
    setState(createInitialFormState());
    const t = window.setTimeout(() => {
      if (variant === "signup") userIdRef.current?.focus();
      else emailRef.current?.focus();
    }, 50);
    return () => window.clearTimeout(t);
  }, [open, variant]);

  const handleBackdropMouseDown = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (e.target === e.currentTarget) onClose();
    },
    [onClose],
  );

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const formProps = formDataToStringRecord(formData);

    void (async () => {
      const notify = (msg: string) => {
        patch({ error: msg });
      };

      patch({ error: null });

      const emailRaw = formProps.email ?? "";
      const password = formProps.password ?? "";
      const passwordConfirm = formProps.passwordConfirm ?? "";
      const userIdRaw = formProps.userId ?? "";
      const nicknameRaw = formProps.nickname ?? "";
      const phoneRaw = formProps.phone ?? "";

      const trimmed = emailRaw.trim();

      if (!trimmed) {
        notify("이메일 주소를 입력해 주세요.");
        return;
      }
      if (!EMAIL_RE.test(trimmed)) {
        notify("올바른 이메일 형식이 아닙니다.");
        return;
      }
      if (!password) {
        notify("비밀번호를 입력해 주세요.");
        return;
      }

      if (variant === "signup") {
        const trimmedUserId = userIdRaw.trim();
        const trimmedNickname = nicknameRaw.trim();
        const phoneDigits = normalizePhone(phoneRaw);

        if (!trimmedUserId) {
          notify("아이디를 입력해 주세요.");
          return;
        }
        if (!USER_ID_RE.test(trimmedUserId)) {
          notify("아이디는 영문·숫자·밑줄(_) 2자 이상으로 입력해 주세요.");
          return;
        }
        if (!trimmedNickname) {
          notify("닉네임을 입력해 주세요.");
          return;
        }
        if (!phoneDigits) {
          notify("휴대전화 번호를 입력해 주세요.");
          return;
        }
        if (!PHONE_RE.test(phoneDigits)) {
          notify("휴대전화 번호 형식이 올바르지 않습니다. (예: 01012345678)");
          return;
        }
        if (password.length < MIN_PASSWORD) {
          notify(`비밀번호는 ${MIN_PASSWORD}자 이상 입력해 주세요.`);
          return;
        }
        if (password !== passwordConfirm) {
          notify("비밀번호가 일치하지 않습니다.");
          return;
        }

        const signupBody = {
          user_id: trimmedUserId,
          email: trimmed,
          nickname: trimmedNickname,
          phone: phoneDigits,
          password,
          password_confirm: passwordConfirm,
        };
        const signupUrl = getSignupUrl();

        patch({ submitting: true });
        try {
          const apiErr = await ensureApiReachable();
          if (apiErr) {
            notify(apiErr);
            return;
          }

          logSignupPayload("API 전송", {
            url: signupUrl,
            body: redactSignupForLog(signupBody),
          });
          const res = await fetch(signupUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(signupBody),
          });
          const raw = await res.text();
          logSignupPayload("API 응답", { status: res.status, body: raw });
          if (!res.ok) {
            notify(parseHttpError(res.status, raw));
            return;
          }
          try {
            JSON.parse(raw);
          } catch {
            notify("회원가입은 성공했으나 서버 응답을 읽지 못했습니다.");
            return;
          }
          onSuccess(trimmed);
          setState(createInitialFormState());
          onClose();
        } catch (err) {
          console.error("[회원가입] API 실패", err);
          const unreachable = await ensureApiReachable();
          notify(
            unreachable ??
              "서버에 연결할 수 없습니다. backend/apps 에서 python main.py 와 frontend 에서 npm run dev 가 모두 실행 중인지 확인하세요.",
          );
        } finally {
          patch({ submitting: false });
        }
        return;
      }

      patch({ submitting: true });
      window.setTimeout(() => {
        patch({ submitting: false });
        onSuccess(trimmed);
        setState(createInitialFormState());
        onClose();
      }, 400);
    })();
  };

  useEffect(() => {
    if (!open) return;
    const onKey = (ev: KeyboardEvent) => {
      if (ev.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  if (!open) return null;

  const isSignup = variant === "signup";
  const title = isSignup ? "회원가입" : "로그인";
  const subtitle = isSignup
    ? "아이디, 이메일, 닉네임, 휴대전화와 비밀번호로 가입합니다."
    : "이메일 주소와 비밀번호로 로그인하세요.";

  return createPortal(
    <div
      className="fixed inset-0 z-[9999] flex flex-col items-center justify-start pt-[max(20px,calc(env(safe-area-inset-top,0px)+16px))] px-4 pb-[max(24px,env(safe-area-inset-bottom,0px))] overflow-x-hidden overflow-y-auto [overscroll-behavior:contain] bg-[rgba(0,0,0,0.65)] backdrop-blur-md"
      role="presentation"
      onMouseDown={handleBackdropMouseDown}
    >
      <div
        className="w-full max-w-[400px] flex-shrink-0 mt-0 mb-6 p-[28px_28px_24px] rounded-2xl bg-[rgba(10,16,32,0.96)] border border-[rgba(0,229,255,0.28)] shadow-[0_0_0_1px_rgba(0,229,255,0.1),0_24px_48px_rgba(0,0,0,0.45)] max-h-[calc(100dvh-48px)] overflow-y-auto"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-3 mb-5">
          <div>
            <h2 id={titleId} className="m-0 text-xl font-extrabold text-white tracking-[-0.02em]">
              {title}
            </h2>
            <p className="mt-[6px] mb-0 text-[13px] leading-[1.5] text-[rgba(203,213,225,0.9)]">
              {subtitle}
            </p>
          </div>
          <button
            type="button"
            className="flex-shrink-0 w-9 h-9 inline-flex items-center justify-center border-none rounded-[10px] bg-[rgba(255,255,255,0.06)] text-[rgba(255,255,255,0.85)] text-2xl leading-none cursor-pointer transition hover:bg-[rgba(0,229,255,0.12)] hover:text-[#00e5ff]"
            onClick={onClose}
            aria-label="닫기"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} noValidate>
          {isSignup ? (
            <>
              <div className={FIELD}>
                <label htmlFor="auth-user-id" className={LABEL}>
                  아이디 (userId)
                </label>
                <input
                  ref={userIdRef}
                  id="auth-user-id"
                  className={INPUT}
                  type="text"
                  name="userId"
                  autoComplete="username"
                  placeholder="영문·숫자·_ 2자 이상"
                  value={state.userId}
                  onChange={(ev) => patch({ userId: ev.target.value })}
                />
              </div>
              <div className={FIELD}>
                <label htmlFor="auth-nickname" className={LABEL}>
                  닉네임
                </label>
                <input
                  id="auth-nickname"
                  className={INPUT}
                  type="text"
                  name="nickname"
                  autoComplete="nickname"
                  placeholder="표시 이름"
                  value={state.nickname}
                  onChange={(ev) => patch({ nickname: ev.target.value })}
                />
              </div>
              <div className={FIELD}>
                <label htmlFor="auth-phone" className={LABEL}>
                  휴대전화
                </label>
                <input
                  id="auth-phone"
                  className={INPUT}
                  type="tel"
                  name="phone"
                  autoComplete="tel"
                  inputMode="tel"
                  placeholder="01012345678"
                  value={state.phone}
                  onChange={(ev) => patch({ phone: ev.target.value })}
                />
              </div>
            </>
          ) : null}
          <div className={FIELD}>
            <label htmlFor="auth-email" className={LABEL}>
              {isSignup ? "이메일" : "이메일 (아이디)"}
            </label>
            <input
              ref={emailRef}
              id="auth-email"
              className={INPUT}
              type="email"
              name="email"
              autoComplete="email"
              inputMode="email"
              placeholder="you@example.com"
              value={state.email}
              onChange={(ev) => patch({ email: ev.target.value })}
            />
          </div>
          <div className={FIELD}>
            <label htmlFor="auth-password" className={LABEL}>
              비밀번호
            </label>
            <input
              id="auth-password"
              className={INPUT}
              type="password"
              name="password"
              autoComplete={isSignup ? "new-password" : "current-password"}
              placeholder="비밀번호"
              value={state.password}
              onChange={(ev) => patch({ password: ev.target.value })}
            />
          </div>
          {isSignup ? (
            <div className={FIELD}>
              <label htmlFor="auth-password2" className={LABEL}>
                비밀번호 확인
              </label>
              <input
                id="auth-password2"
                className={INPUT}
                type="password"
                name="passwordConfirm"
                autoComplete="new-password"
                placeholder="비밀번호 다시 입력"
                value={state.passwordConfirm}
                onChange={(ev) => patch({ passwordConfirm: ev.target.value })}
              />
            </div>
          ) : null}
          {state.error ? (
            <p className="mt-[-8px] mb-[14px] text-[13px] text-[#fecaca] leading-[1.45]" role="alert">
              {state.error}
            </p>
          ) : null}
          <button
            type="submit"
            className="w-full mt-2 p-[14px_20px] border-none rounded-full font-extrabold text-[15px] tracking-[0.02em] cursor-pointer bg-[#00e5ff] text-[#04131a] transition enabled:hover:bg-[#33ebff] enabled:hover:-translate-y-px disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={state.submitting}
          >
            {state.submitting ? "처리 중…" : isSignup ? "회원가입" : "로그인"}
          </button>
          <p className="mt-4 mb-0 text-xs leading-[1.5] text-[rgba(148,163,184,0.85)] text-center">
            {isSignup
              ? "회원가입 시 POST /signup 으로 전송됩니다. 터미널에서 수신 로그를 확인하세요."
              : "데모 로그인입니다."}
          </p>
          {!isSignup ? (
            <div className="mt-5 pt-5 border-t border-[rgba(148,163,184,0.15)]">
              <p className="mb-3 text-xs font-bold tracking-[0.04em] text-[rgba(148,163,184,0.85)] text-center">
                간편 로그인
              </p>
              <div className="flex flex-col gap-2">
                {SOCIAL_PROVIDERS.map((provider) => {
                  const Icon = provider.icon;
                  return (
                    <button
                      key={provider.id}
                      type="button"
                      className="w-full p-[12px_16px] rounded-full font-bold text-sm cursor-pointer transition hover:opacity-90 inline-flex items-center justify-center gap-2"
                      style={provider.style}
                      onClick={() => handleSocialClick(provider)}
                    >
                      {Icon ? <Icon /> : null}
                      {provider.label}
                    </button>
                  );
                })}
              </div>
            </div>
          ) : null}
        </form>
      </div>
    </div>,
    document.body,
  );
}
