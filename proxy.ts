import { NextResponse } from "next/server"
import { auth } from "@/auth"

// Next.js 16 llama "proxy" a lo que antes era middleware.ts: corre antes de
// servir cualquier ruta, incluidos los archivos estáticos de public/.
// Sin sesión, todo el sitio (portal, dashboards, meetings.json) redirige a /login.
export default auth((req) => {
  if (req.auth) return

  const login = new URL("/login", req.nextUrl.origin)
  const destino = req.nextUrl.pathname + req.nextUrl.search
  if (destino !== "/") login.searchParams.set("callbackUrl", destino)
  return NextResponse.redirect(login)
})

export const config = {
  // Todo menos el login, las rutas de Auth.js y los assets internos de Next.
  matcher: ["/((?!api/auth|login|_next/static|_next/image|favicon.ico).*)"],
}
