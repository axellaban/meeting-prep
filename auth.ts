import NextAuth from "next-auth"
import Google from "next-auth/providers/google"

// Las credenciales salen solo del entorno (ver .env.example):
//   AUTH_GOOGLE_ID y AUTH_GOOGLE_SECRET los toma el provider de Google,
//   AUTH_SECRET firma y cifra la sesión.
export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Google({
      clientId: process.env.AUTH_GOOGLE_ID,
      clientSecret: process.env.AUTH_GOOGLE_SECRET,
      // Solo los scopes básicos: identidad, mail y perfil.
      authorization: { params: { scope: "openid email profile" } },
    }),
  ],
  secret: process.env.AUTH_SECRET,
  pages: {
    signIn: "/login",
    error: "/login",
  },
})
