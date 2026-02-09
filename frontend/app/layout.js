import './globals.css'

export const metadata = {
    title: 'Balk FEM Solver',
    description: 'Web GUI for Balk FEM Solver',
}

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <body>{children}</body>
        </html>
    )
}
