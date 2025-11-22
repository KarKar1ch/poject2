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
      "rounded-[30px] bg-white text-card-foreground shadow-sm",
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
      "text-2xl font-semibold leading-none tracking-tight",
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
    className={cn("text-sm text-muted-foreground", className)}
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