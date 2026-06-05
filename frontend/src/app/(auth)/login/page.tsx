"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { ArrowRight, Mail, Lock, Eye, EyeOff, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/use-auth";

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormValues) => {
    setIsLoading(true);
    try {
      await login(data);
      router.push("/");
      router.refresh();
    } catch (error) {
      setError("root", {
        message: error instanceof Error ? error.message : "Unable to sign in",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col w-full">
      {/* Header */}
      <div className="mb-10 sm:mb-12">
        <h2 className="text-4xl sm:text-5xl font-display font-black tracking-tighter text-foreground leading-tight">
          Welcome <br className="hidden sm:block" />
          <span className="text-primary-700">back.</span>
        </h2>
        <p className="text-lg text-neutral-500 font-medium">
          Sign in to your account to continue booking.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5" noValidate>
        {/* Root Error */}
        {errors.root && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-sm text-red-600 dark:text-red-400 font-medium flex items-start gap-2.5">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-red-500 shrink-0 mt-1.5" />
            <p>{errors.root.message}</p>
          </div>
        )}
        {/* Email */}
        <div className="flex flex-col gap-2">
          <Label htmlFor="login-email" className="text-sm font-semibold text-foreground">Email address</Label>
          <div className="relative group">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400 group-focus-within:text-primary-500 transition-colors" />
            <Input
              id="login-email"
              type="email"
              placeholder="name@example.com"
              className="pl-12 h-14 text-base font-medium border-2 border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900 focus:bg-white dark:focus:bg-neutral-950 rounded-xl focus:border-primary-500 focus:ring-0 transition-all outline-none"
              autoComplete="email"
              {...register("email")}
              disabled={isLoading}
            />
          </div>
          {errors.email && (
            <p className="text-sm text-red-500 flex items-center gap-1">
              <span className="inline-block w-1 h-1 rounded-full bg-red-500" />
              {errors.email.message}
            </p>
          )}
        </div>

        {/* Password */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="login-password" className="text-sm font-semibold text-foreground">Password</Label>
            <Link
              href="/forgot-password"
              className="text-sm text-primary-600 hover:text-primary-700 font-bold transition-colors"
            >
              Forgot password?
            </Link>
          </div>
          <div className="relative group">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400 group-focus-within:text-primary-500 transition-colors" />
            <Input
              id="login-password"
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              className="pl-12 pr-12 h-14 text-base font-medium border-2 border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900 focus:bg-white dark:focus:bg-neutral-950 rounded-xl focus:border-primary-500 focus:ring-0 transition-all outline-none"
              autoComplete="current-password"
              {...register("password")}
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-md p-1"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? (
                <EyeOff className="h-5 w-5" />
              ) : (
                <Eye className="h-5 w-5" />
              )}
            </button>
          </div>
          {errors.password && (
            <p className="text-sm text-red-500 flex items-center gap-1">
              <span className="inline-block w-1 h-1 rounded-full bg-red-500" />
              {errors.password.message}
            </p>
          )}
        </div>

        {/* Submit */}
        <Button
          type="submit"
          className="w-full h-14 text-lg font-bold bg-primary-800 hover:bg-primary-700 text-white rounded-xl shadow-sm transition-all active:scale-[0.98] mt-2"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Signing in...
            </>
          ) : (
            <>
              Sign in
              <ArrowRight className="ml-2 h-5 w-5" />
            </>
          )}
        </Button>
      </form>

      {/* Divider */}
      <div className="relative mt-10 mb-8">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-3 text-neutral-500 font-semibold tracking-wider">
            New to BusYatra?
          </span>
        </div>
      </div>

      <Link href="/register" className="block">
        <Button variant="outline" className="w-full h-14 text-lg font-semibold border-2 border-neutral-200 dark:border-neutral-800 rounded-xl hover:bg-neutral-50 dark:hover:bg-neutral-900 text-foreground transition-colors">
          Create a free account
        </Button>
      </Link>
    </div>
  );
}
