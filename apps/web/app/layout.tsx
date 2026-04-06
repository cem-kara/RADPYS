import type { ReactNode } from "react";

import "./globals.css";

export const metadata = {
  title: "REPYS Next",
  description: "REPYS Next web experience",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
