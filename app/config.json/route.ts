import config from "../../config.json"

// El portal lee config.json para la marca y los textos. El archivo se queda en la
// raíz porque el pipeline y las skills lo leen ahí; esta ruta lo sirve (detrás del login).
export function GET() {
  return Response.json(config)
}
