import * as React from "react"

const ToastProvider = ({ children }: { children: React.ReactNode }) => {
    return <div className="fixed top-0 right-0 p-4 z-50">{children}</div>
}

const ToastViewport = React.forwardRef<
    HTMLOListElement,
    React.HTMLAttributes<HTMLOListElement>
>(({ className, ...props }, ref) => (
    <ol
        ref={ref}
        className="flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]"
        {...props}
    />
))
ToastViewport.displayName = "ToastViewport"

const Toast = React.forwardRef<
    HTMLLIElement,
    React.HTMLAttributes<HTMLLIElement>
>(({ className, ...props }, ref) => {
    return (
        <li className="bg-white border rounded p-4 shadow mb-2" ref={ref} {...props} />
    )
})
Toast.displayName = "Toast"

const ToastTitle = React.forwardRef<
    HTMLHeadingElement,
    React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
    <div className="font-semibold text-sm" ref={ref} {...props} />
))
ToastTitle.displayName = "ToastTitle"

const ToastDescription = React.forwardRef<
    HTMLParagraphElement,
    React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
    <div className="text-sm opacity-90" ref={ref} {...props} />
))
ToastDescription.displayName = "ToastDescription"

const ToastClose = React.forwardRef<
    HTMLButtonElement,
    React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, ...props }, ref) => (
    <button className="absolute right-2 top-2 rounded-md p-1 text-foreground/50 opacity-0 transition-opacity hover:text-foreground focus:opacity-100 focus:outline-none focus:ring-2 group-hover:opacity-100" ref={ref} {...props}>
        X
    </button>
))
ToastClose.displayName = "ToastClose"

type ToastProps = React.ComponentPropsWithoutRef<typeof Toast>
type ToastActionElement = React.ReactElement

export interface ToastMessage {
    id: string
    type: "success" | "error" | "warning" | "info"
    message: string
}

export const ToastContainer = ({ toasts, removeToast }: { toasts: ToastMessage[], removeToast: (id: string) => void }) => {
    return (
        <ToastProvider>
            {toasts.map(t => (
                <Toast key={t.id} className={`mb-2 ${t.type === 'error' ? 'bg-red-100 border-red-500' : 'bg-white'}`}>
                    <div className="flex justify-between items-center">
                        <ToastDescription>{t.message}</ToastDescription>
                        <ToastClose onClick={() => removeToast(t.id)} />
                    </div>
                </Toast>
            ))}
            <ToastViewport />
        </ToastProvider>
    )
}

export {
    ToastProvider,
    ToastViewport,
    Toast,
    ToastTitle,
    ToastDescription,
    ToastClose,
    type ToastProps,
    type ToastActionElement,
}
