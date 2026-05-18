"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/navbar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  MapPin,
  Calendar,
  ArrowRightLeft,
  ShieldCheck,
  HeadphonesIcon,
  Ticket,
  Bus,
  Star,
  Clock,
  ArrowRight,
  Zap,
  Users,
  Route,
} from "lucide-react";

/* ─── Static data (no API yet) ─── */
const POPULAR_ROUTES = [
  { from: "Delhi", to: "Jaipur", duration: "5h 30m", price: "₹450", trips: 42 },
  { from: "Mumbai", to: "Pune", duration: "3h 45m", price: "₹350", trips: 56 },
  { from: "Bangalore", to: "Chennai", duration: "6h 15m", price: "₹600", trips: 38 },
  { from: "Hyderabad", to: "Goa", duration: "10h 00m", price: "₹850", trips: 24 },
  { from: "Lucknow", to: "Varanasi", duration: "4h 30m", price: "₹400", trips: 30 },
  { from: "Ahmedabad", to: "Udaipur", duration: "5h 00m", price: "₹500", trips: 22 },
];

const STATS = [
  { icon: Route, value: "1,000+", label: "Destinations" },
  { icon: Bus, value: "5,000+", label: "Daily Buses" },
  { icon: Users, value: "2M+", label: "Happy Travellers" },
  { icon: Star, value: "4.8", label: "Avg Rating" },
] as const;

export default function HomePage() {
  const router = useRouter();
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [date, setDate] = useState("");

  const handleSwap = () => {
    const temp = from;
    setFrom(to);
    setTo(temp);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (from && to && date) {
      router.push(
        `/search?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}&date=${date}`
      );
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* ── HERO ── */}
      <section className="relative min-h-[600px] lg:min-h-[680px] flex flex-col">
        {/* Background — single flat surface with one subtle gradient for depth */}
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-primary-900" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,var(--color-primary-800)_0%,var(--color-primary-900)_70%)]" />
          {/* Bottom fade into page bg */}
          <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-background/0" />
        </div>

        {/* Navbar — sits on top of hero */}
        <div className="relative z-20">
          <Navbar />
        </div>

        {/* Hero content */}
        <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-4 sm:px-6 pt-8 pb-24 lg:pb-32">
          <div className="text-center max-w-3xl mx-auto mb-10 lg:mb-14">
            <div className="inline-flex items-center gap-2 bg-primary-800 border border-primary-700 rounded-full px-4 py-1.5 mb-6">
              <Zap className="w-3.5 h-3.5 text-accent-400" />
              <span className="text-sm text-white/90 font-medium">
                Instant booking confirmation
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-display font-black text-white leading-[1.1] tracking-tighter mb-6">
              Your next journey
              <br />
              <span className="text-accent-400">starts here.</span>
            </h1>

            <p className="text-lg sm:text-xl text-primary-200 max-w-xl mx-auto leading-snug">
              Search, compare, and book bus tickets across India at the lowest
              prices — guaranteed.
            </p>
          </div>

          {/* ── Search Widget ── */}
          <div className="w-full max-w-4xl mx-auto">
            <div className="bg-card rounded-2xl border-2 border-neutral-200 dark:border-neutral-800 p-5 sm:p-6">
              <form
                onSubmit={handleSearch}
                className="flex flex-col lg:flex-row items-stretch gap-3"
                noValidate
              >
                {/* From / To group */}
                <div className="flex-1 flex flex-col sm:flex-row items-stretch gap-3 relative">
                  {/* From */}
                  <div className="flex-1 relative group">
                    <Label htmlFor="hero-from" className="sr-only">
                      Leaving from
                    </Label>
                    <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-primary-500 z-10" />
                    <Input
                      id="hero-from"
                      value={from}
                      onChange={(e) => setFrom(e.target.value)}
                      placeholder="Leaving from"
                      className="pl-12 h-14 text-base font-medium border-2 border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900 focus:bg-white dark:focus:bg-neutral-950 rounded-xl focus:border-primary-500 focus:ring-0 transition-all outline-none"
                      required
                    />
                  </div>

                  {/* Swap — desktop (floating) */}
                  <div className="hidden sm:flex absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-20">
                    <button
                      type="button"
                      onClick={handleSwap}
                      aria-label="Swap departure and destination"
                      className="w-10 h-10 rounded-full bg-card border-2 border-neutral-200 dark:border-neutral-800 flex items-center justify-center text-neutral-500 hover:text-primary-600 hover:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all hover:scale-105 active:scale-95"
                    >
                      <ArrowRightLeft className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Swap — mobile (inline between fields) */}
                  <div className="flex sm:hidden justify-center -my-1">
                    <button
                      type="button"
                      onClick={handleSwap}
                      aria-label="Swap departure and destination"
                      className="w-9 h-9 rounded-full bg-card border-2 border-neutral-200 dark:border-neutral-800 flex items-center justify-center text-neutral-500 hover:text-primary-600 hover:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all active:scale-95 rotate-90"
                    >
                      <ArrowRightLeft className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {/* To */}
                  <div className="flex-1 relative group">
                    <Label htmlFor="hero-to" className="sr-only">
                      Going to
                    </Label>
                    <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-accent-500 z-10" />
                    <Input
                      id="hero-to"
                      value={to}
                      onChange={(e) => setTo(e.target.value)}
                      placeholder="Going to"
                      className="pl-12 h-14 text-base font-medium border-2 border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900 focus:bg-white dark:focus:bg-neutral-950 rounded-xl focus:border-primary-500 focus:ring-0 transition-all outline-none"
                      required
                    />
                  </div>
                </div>

                {/* Date */}
                <div className="lg:w-[200px] relative group">
                  <Label htmlFor="hero-date" className="sr-only">
                    Date of Journey
                  </Label>
                  <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-primary-500 z-10" />
                  <Input
                    id="hero-date"
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="pl-12 h-14 text-base font-medium border-2 border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900 focus:bg-white dark:focus:bg-neutral-950 rounded-xl focus:border-primary-500 focus:ring-0 transition-all outline-none"
                    required
                  />
                </div>

                {/* Search button */}
                <Button
                  type="submit"
                  className="h-14 px-8 text-lg font-display font-bold bg-primary-800 hover:bg-primary-700 text-white rounded-xl transition-all active:scale-[0.98] whitespace-nowrap"
                >
                  Search Buses
                </Button>
              </form>
            </div>
          </div>

          {/* ── Trust Stats ── */}
          <div className="w-full max-w-4xl mx-auto mt-8">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-6">
              {STATS.map((stat) => (
                <div key={stat.label} className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary-800/80 border border-primary-700/50 flex items-center justify-center shrink-0">
                    <stat.icon className="w-5 h-5 text-primary-300" />
                  </div>
                  <div>
                    <p className="text-lg font-display font-bold text-white leading-none">
                      {stat.value}
                    </p>
                    <p className="text-xs text-primary-300 font-medium mt-0.5">
                      {stat.label}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── POPULAR ROUTES ── */}
      <section className="py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-end justify-between mb-10">
            <div>
              <h2 className="text-2xl sm:text-3xl font-display font-bold text-foreground">
                Popular Routes
              </h2>
              <p className="mt-2 text-neutral-500">
                Most booked routes this month
              </p>
            </div>
            <Link
              href="/routes"
              className="hidden sm:flex items-center gap-1.5 text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
            >
              View all routes
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {POPULAR_ROUTES.map((route) => (
              <Link
                key={`${route.from}-${route.to}`}
                href={`/search?from=${route.from}&to=${route.to}`}
                className="group bg-card rounded-xl border-2 border-neutral-200 dark:border-neutral-800 p-5 hover:shadow-md hover:border-primary-500 transition-all active:scale-[0.98]"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="font-display font-semibold text-foreground">
                      {route.from}
                    </span>
                    <ArrowRight className="w-4 h-4 text-neutral-400 group-hover:text-primary-500 transition-colors" />
                    <span className="font-display font-semibold text-foreground">
                      {route.to}
                    </span>
                  </div>
                  <span className="text-lg font-mono font-bold text-primary-600">
                    {route.price}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-sm text-neutral-500">
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{route.duration}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Bus className="w-3.5 h-3.5" />
                    <span>{route.trips} buses daily</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── WHY BUSYATRA ── */}
      <section className="py-16 sm:py-20 border-t border-border bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row gap-12 lg:gap-24 items-start">
            <div className="lg:w-1/3 sticky top-24">
              <h2 className="text-3xl font-display font-bold text-foreground leading-tight">
                Built for <br />confidence.
              </h2>
              <p className="mt-4 text-neutral-500 text-lg">
                We're building the most trusted bus travel platform in India, prioritizing verified operators and 24/7 support.
              </p>
            </div>

            <div className="lg:w-2/3 flex flex-col gap-10">
              {[
                {
                  icon: ShieldCheck,
                  title: "Verified Operators",
                  desc: "Every bus operator is background-checked and verified before they can list on our platform. Your safety is guaranteed.",
                },
                {
                  icon: Ticket,
                  title: "Best Prices",
                  desc: "We negotiate directly with operators to offer you exclusive deals you won't find anywhere else. Transparent pricing, no hidden fees.",
                },
                {
                  icon: HeadphonesIcon,
                  title: "24/7 Support",
                  desc: "Our support team is available round the clock via call, chat, or email — even during your trip.",
                },
              ].map((feature, index) => (
                <div
                  key={feature.title}
                  className={`flex gap-6 items-start ${index !== 0 ? "pt-10 border-t border-border" : ""}`}
                >
                  <div className="w-14 h-14 rounded-xl bg-primary-50 dark:bg-primary-900/20 border border-primary-100 dark:border-primary-800/50 flex items-center justify-center shrink-0">
                    <feature.icon className="w-7 h-7 text-primary-700 dark:text-primary-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-display font-semibold text-foreground mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-neutral-500 leading-relaxed text-lg">
                      {feature.desc}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA BANNER ── */}
      <section className="py-16 sm:py-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-primary-900 rounded-2xl p-10 sm:p-14 text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,var(--color-primary-800)_0%,var(--color-primary-900)_70%)]" />

            <div className="relative z-10">
              <h2 className="text-2xl sm:text-3xl font-display font-bold text-white mb-4">
                Ready to start your journey?
              </h2>
              <p className="text-primary-200 max-w-md mx-auto mb-8">
                Create a free account and get access to exclusive deals,
                instant booking, and seamless trip management.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
                <Link href="/register">
                  <Button
                    className="h-14 px-8 text-lg font-display bg-accent-500 hover:bg-accent-600 text-neutral-900 font-bold transition-all active:scale-[0.98]"
                  >
                    Sign up for free
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>
                </Link>
                <Link href="/login">
                  <Button
                    variant="ghost"
                    className="h-14 px-8 text-lg font-display text-white hover:bg-white/10 font-bold transition-all active:scale-[0.98]"
                  >
                    I already have an account
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="bg-neutral-800 border-t border-neutral-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-10">
            {/* Brand */}
            <div className="col-span-2 md:col-span-1">
              <div className="flex items-center gap-2.5 mb-4">
                <div className="w-9 h-9 bg-primary-500 rounded-xl flex items-center justify-center">
                  <Bus className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-display font-bold text-white">
                  BusYatra
                </span>
              </div>
              <p className="text-neutral-400 text-sm leading-relaxed">
                India's premier bus booking platform. Safe, affordable, and
                always on time.
              </p>
            </div>

            {/* Links */}
            <div>
              <h3 className="text-sm font-display font-semibold text-white mb-4">Company</h3>
              <ul className="space-y-2.5 text-sm text-neutral-400">
                <li>
                  <Link href="/about" className="hover:text-white transition-colors">
                    About Us
                  </Link>
                </li>
                <li>
                  <Link href="/careers" className="hover:text-white transition-colors">
                    Careers
                  </Link>
                </li>
                <li>
                  <Link href="/blog" className="hover:text-white transition-colors">
                    Blog
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-display font-semibold text-white mb-4">Support</h3>
              <ul className="space-y-2.5 text-sm text-neutral-400">
                <li>
                  <Link href="/help" className="hover:text-white transition-colors">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link href="/contact" className="hover:text-white transition-colors">
                    Contact Us
                  </Link>
                </li>
                <li>
                  <Link href="/faq" className="hover:text-white transition-colors">
                    FAQs
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-display font-semibold text-white mb-4">Legal</h3>
              <ul className="space-y-2.5 text-sm text-neutral-400">
                <li>
                  <Link href="/terms" className="hover:text-white transition-colors">
                    Terms of Service
                  </Link>
                </li>
                <li>
                  <Link href="/privacy" className="hover:text-white transition-colors">
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link href="/refund-policy" className="hover:text-white transition-colors">
                    Refund Policy
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-neutral-700 pt-8 text-center text-sm text-neutral-500">
            © {new Date().getFullYear()} BusYatra. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
