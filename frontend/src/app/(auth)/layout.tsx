import React from "react";
import Link from "next/link";
import { Bus } from "lucide-react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex w-full bg-background">
      {/* Left side — brand showcase */}
      <div className="hidden lg:flex w-[55%] relative overflow-hidden">
        {/* Layered background */}
        <div className="absolute inset-0 bg-primary-900" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,var(--color-primary-700)_0%,transparent_50%)]" />

        {/* Dot grid pattern for texture */}
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage:
              "radial-gradient(circle, white 1px, transparent 1px)",
            backgroundSize: "24px 24px",
          }}
        />

        <div className="relative z-10 flex flex-col justify-between p-12 xl:p-16 w-full">
          {/* Top: Brand */}
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20">
              <Bus className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-display font-bold text-white tracking-tight">
              BusYatra
            </span>
          </Link>

          {/* Center: Hero copy */}
          <div className="max-w-md space-y-6">
            <h1 className="text-4xl xl:text-5xl font-display font-bold text-white leading-[1.15]">
              Travel smarter.
              <br />
              <span className="text-accent-400">Book faster.</span>
            </h1>
            <p className="text-primary-200 text-lg leading-relaxed">
              Join millions of travellers who book comfortable, affordable bus
              journeys across India with BusYatra.
            </p>

          </div>

          {/* Spacer to keep vertical alignment balanced */}
          <div />
        </div>
      </div>

      {/* Right side — form */}
      <div className="w-full lg:w-[45%] flex flex-col">
        {/* Mobile header */}
        <div className="lg:hidden flex items-center justify-between p-6 border-b border-border">
          <Link
            href="/"
            className="flex items-center gap-2 font-display font-bold text-foreground"
          >
            <div className="bg-primary-500 text-white p-1.5 rounded-lg">
              <Bus className="w-5 h-5" />
            </div>
            <span className="text-xl tracking-tight">BusYatra</span>
          </Link>
        </div>

        {/* Form content — vertically centered */}
        <div className="flex-1 flex items-center justify-center p-6 sm:p-10 lg:p-16">
          <div className="w-full max-w-[480px]">{children}</div>
        </div>
      </div>
    </div>
  );
}
