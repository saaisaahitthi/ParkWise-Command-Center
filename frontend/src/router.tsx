import { lazy, Suspense } from "react";
import { createBrowserRouter, Navigate } from "react-router-dom";
import { AppShell } from "@/layout/AppShell";

// Lazy-load every page for code-splitting
const Dashboard  = lazy(() => import("@/pages/Dashboard"));
const Hotspots   = lazy(() => import("@/pages/Hotspots"));
const Temporal   = lazy(() => import("@/pages/Temporal"));
const Forecast   = lazy(() => import("@/pages/Forecast"));
const Officers   = lazy(() => import("@/pages/Officers"));
const Patrol     = lazy(() => import("@/pages/Patrol"));
const Landing    = lazy(() => import("@/pages/Landing"));
const NotFound   = lazy(() => import("@/pages/NotFound"));

// Full-page loading fallback
function PageLoader() {
  return (
    <div className="flex h-64 items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-blue-500" />
    </div>
  );
}

function Lazy({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<PageLoader />}>{children}</Suspense>;
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      // Default redirect
      { index: true, element: <Navigate to="/landing" replace /> },

      // App pages
      { path: "dashboard",  element: <Lazy><Dashboard /></Lazy> },
      { path: "hotspots",   element: <Lazy><Hotspots /></Lazy> },
      { path: "temporal",   element: <Lazy><Temporal /></Lazy> },
      { path: "forecast",   element: <Lazy><Forecast /></Lazy> },
      { path: "officers",   element: <Lazy><Officers /></Lazy> },
      { path: "patrol",     element: <Lazy><Patrol /></Lazy> },
      { path: "landing",   element: <Lazy><Landing /></Lazy> },

      // Catch-all
      { path: "*", element: <Lazy><NotFound /></Lazy> },
    ],
  },
]);
