"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { ReactNode } from "react";

export function Providers({ children }: { children: ReactNode }) {
  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      // CopilotKit configuration
      showDevConsole={false} // Disabled to reduce UI clutter in development
    >
      {children}
    </CopilotKit>
  );
}
