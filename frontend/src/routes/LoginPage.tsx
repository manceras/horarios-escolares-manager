import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";

import { QueryState } from "@/components/QueryState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, storeToken } from "@/lib/api/client";

export function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<unknown>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit(): Promise<void> {
    setError(null);
    setIsSubmitting(true);

    const { data, error: loginError } = await api.POST("/api/v1/auth/login", {
      body: { email, password },
    });
    setIsSubmitting(false);

    if (loginError) {
      setError(loginError);
      return;
    }
    storeToken(data.access_token);
    void navigate("/teachers");
  }

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        void submit();
      }}
      className="mx-auto mt-24 w-full max-w-sm space-y-4"
    >
      <h1 className="text-xl font-semibold">{t("login.title")}</h1>
      <label className="block space-y-1 text-sm">
        <span>{t("login.email")}</span>
        <Input
          type="email"
          value={email}
          autoComplete="username"
          onChange={(event) => {
            setEmail(event.target.value);
          }}
          required
        />
      </label>
      <label className="block space-y-1 text-sm">
        <span>{t("login.password")}</span>
        <Input
          type="password"
          value={password}
          autoComplete="current-password"
          onChange={(event) => {
            setPassword(event.target.value);
          }}
          required
        />
      </label>
      <QueryState isLoading={false} error={error} />
      <Button type="submit" disabled={isSubmitting} className="w-full">
        {t("login.submit")}
      </Button>
    </form>
  );
}
