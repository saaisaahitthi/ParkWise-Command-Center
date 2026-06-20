import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { LayoutDashboard } from "lucide-react";

export default function NotFoundPage() {
  return (
    <div className="flex h-full min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <p className="text-6xl font-bold text-slate-200">404</p>
      <h2 className="text-xl font-semibold text-slate-700">Page not found</h2>
      <p className="text-sm text-slate-500">
        This route doesn't exist in the command center.
      </p>
      <Button asChild variant="outline" className="mt-2">
        <Link to="/dashboard">
          <LayoutDashboard className="h-4 w-4" />
          Back to Dashboard
        </Link>
      </Button>
    </div>
  );
}
