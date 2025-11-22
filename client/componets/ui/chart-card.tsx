"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

// ChartCard компоненты
const ChartCard = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-[30px] bg-white text-card-foreground shadow-sm border border-slate-100",
      className
    )}
    {...props}
  />
))
ChartCard.displayName = "ChartCard"

const ChartCardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
))
ChartCardHeader.displayName = "ChartCardHeader"

const ChartCardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-lg font-bold text-slate-900",
      className
    )}
    {...props}
  />
))
ChartCardTitle.displayName = "ChartCardTitle"

const ChartCardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm font-medium text-slate-400 mt-1", className)}
    {...props}
  />
))
ChartCardDescription.displayName = "ChartCardDescription"

const ChartCardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
ChartCardContent.displayName = "ChartCardContent"

const ChartCardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
ChartCardFooter.displayName = "ChartCardFooter"

export {
  ChartCard,
  ChartCardHeader,
  ChartCardFooter,
  ChartCardTitle,
  ChartCardDescription,
  ChartCardContent,
}