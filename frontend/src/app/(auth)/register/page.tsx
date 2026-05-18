"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  ArrowRight,
  Mail,
  Lock,
  User,
  Phone,
  Eye,
  EyeOff,
  Loader2,
  Check,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const registerSchema = z
  .object({
    name: z.string().min(2, "Name must be at least 2 characters"),
    email: z.string().email("Please enter a valid email address"),
    phone: z
      .string()
      .regex(/^\d{10}$/, "Phone number must be 10 digits")
      .optional()
      .or(z.literal("")),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

type RegisterFormValues = z.infer<typeof registerSchema>;

// Password strength indicator
function PasswordStrength({ password }: { password: string }) {
  const checks = [
    { label: "8+ characters", met: password.length >= 8 },
    { label: "Uppercase letter", met: /[A-Z]/.test(password) },
    { label: "Number", met: /\d/.test(password) },
  ];

  if (!password) return null;

  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2">
      {checks.map((check) => (
        <div key={check.label} className="flex items-center gap-1.5 text-xs">
          <div
            className={`w-3.5 h-3.5 rounded-full flex items-center justify-center transition-colors ${
              check.met
                ? "bg-seat-available/20 text-seat-available"
                : "bg-neutral-200 text-neutral-400 dark:bg-neutral-700 dark:text-neutral-500"
            }`}
          >
            {check.met && <Check className="w-2.5 h-2.5" />}
          </div>
          <span
            className={
              check.met
                ? "text-neutral-600 dark:text-neutral-300"
                : "text-neutral-400"
            }
          >
            {check.label}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function RegisterPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  });

  const passwordValue = watch("password", "");

  const onSubmit = async (data: RegisterFormValues) => {
    setIsLoading(true);
    // TODO: Wire to Apollo mutation
    setTimeout(() => {
      console.log("Registration submitted:", data);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="flex flex-col w-full">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl sm:text-4xl font-display font-black tracking-tighter text-foreground leading-tight">
          Create your <span className="text-accent-500">account.</span>
        </h2>
        <p className="text-base text-neutral-500 font-medium mt-2">
          Start booking buses across India in under a minute.
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
        {/* Name */}
        <div className="flex flex-col gap-2">
          <Label htmlFor="reg-name" className="text-sm font-semibold text-foreground">Full Name</Label>
          <div className="relative group">
            <User className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400 group-focus-within:text-primary-500 transition-colors" />
            <Input
              id="reg-name"
              placeholder="Rahul Sharma"
              className="pl-12 h-14 text-base font-medium border-2 border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900 focus:bg-white dark:focus:bg-neutral-950 rounded-xl focus:border-primary-500 focus:ring-0 transition-all outline-none"
              autoComplete="name"
              {...register("name")}
              disabled={isLoading}
            />
          </div>
          {errors.name && (
            <p className="text-sm text-red-500 flex items-center gap-1">
              <span className="inline-block w-1 h-1 rounded-full bg-red-500" />
              {errors.name.message}
            </p>
          )}
        </div>

        {/* Email & Phone — side by side on larger screens */}
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="flex flex-col gap-2">
            <Label htmlFor="reg-email" className="text-sm font-semibold text-foreground">Email</Label>
            <div className="relative group">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400 group-focus-within:text-primary-500 transition-colors" />
              <Input
                id="reg-email"
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

          <div className="flex flex-col gap-2">
            <Label htmlFor="reg-phone" className="text-sm font-semibold text-foreground">
              Phone{" "}
              <span className="text-neutral-400 font-normal">(optional)</span>
            </Label>
            <div className="relative group">
              <Phone className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400 group-focus-within:text-primary-500 transition-colors" />
              <Input
                id="reg-phone"
                type="tel"
                placeholder="9876543210"
                className="pl-12 h-14 text-base font-medium border-2 border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900 focus:bg-white dark:focus:bg-neutral-950 rounded-xl focus:border-primary-500 focus:ring-0 transition-all outline-none"
                autoComplete="tel"
                {...register("phone")}
                disabled={isLoading}
              />
            </div>
            {errors.phone && (
              <p className="text-sm text-red-500 flex items-center gap-1">
                <span className="inline-block w-1 h-1 rounded-full bg-red-500" />
                {errors.phone.message}
              </p>
            )}
          </div>
        </div>

        {/* Password Group */}
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="flex flex-col gap-2">
            <Label htmlFor="reg-password" className="text-sm font-semibold text-foreground">Password</Label>
            <div className="relative group">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400 group-focus-within:text-primary-500 transition-colors" />
              <Input
                id="reg-password"
                type={showPassword ? "text" : "password"}
                placeholder="Strong password"
                className="pl-12 pr-12 h-14 text-base font-medium border-2 border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900 focus:bg-white dark:focus:bg-neutral-950 rounded-xl focus:border-primary-500 focus:ring-0 transition-all outline-none"
                autoComplete="new-password"
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
                <span className="inline-block w-1 h-1 rounded-full bg-red-500 shrink-0" />
                {errors.password.message}
              </p>
            )}
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="reg-confirm" className="text-sm font-semibold text-foreground">Confirm</Label>
            <div className="relative group">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400 group-focus-within:text-primary-500 transition-colors" />
              <Input
                id="reg-confirm"
                type="password"
                placeholder="Re-enter password"
                className="pl-12 h-14 text-base font-medium border-2 border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900 focus:bg-white dark:focus:bg-neutral-950 rounded-xl focus:border-primary-500 focus:ring-0 transition-all outline-none"
                autoComplete="new-password"
                {...register("confirmPassword")}
                disabled={isLoading}
              />
            </div>
            {errors.confirmPassword && (
              <p className="text-sm text-red-500 flex items-center gap-1">
                <span className="inline-block w-1 h-1 rounded-full bg-red-500 shrink-0" />
                {errors.confirmPassword.message}
              </p>
            )}
          </div>
        </div>
        <PasswordStrength password={passwordValue} />

        {/* Terms notice */}
        <p className="text-xs text-neutral-400 leading-relaxed">
          By creating an account, you agree to our{" "}
          <Link
            href="/terms"
            className="text-primary-600 hover:underline font-medium"
          >
            Terms of Service
          </Link>{" "}
          and{" "}
          <Link
            href="/privacy"
            className="text-primary-600 hover:underline font-medium"
          >
            Privacy Policy
          </Link>
          .
        </p>

        {/* Submit */}
        <Button
          type="submit"
          className="w-full h-14 text-lg font-bold bg-primary-800 hover:bg-primary-700 text-white rounded-xl shadow-sm transition-all active:scale-[0.98] mt-2"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Creating account...
            </>
          ) : (
            <>
              Create account
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
            Already registered?
          </span>
        </div>
      </div>

      <Link href="/login" className="block">
        <Button
          variant="outline"
          className="w-full h-14 text-lg font-semibold border-2 border-neutral-200 dark:border-neutral-800 rounded-xl hover:bg-neutral-50 dark:hover:bg-neutral-900 text-foreground transition-colors"
        >
          Sign in to your account
        </Button>
      </Link>
    </div>
  );
}
