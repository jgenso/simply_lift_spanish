package bootstrap.liftweb

import net.liftweb._
import util._
import Helpers._

import common._
import http._
import sitemap._
import Loc._

import code.snippet._

/**
 * Una clase que es instanciada tempranamente y luego ejecutada. Permite que la aplicación 
 * modifique el entorno de Lift
 */
class Boot {
  /**
   * Calcula si la página debe ser mostrada.
   * En este caso, será visible cada minuto
   */
  def displaySometimes_? : Boolean = 
    (millis / 1000L / 60L) % 2 == 0

  def boot {
    // Donde se debe buscar el snippet
    LiftRules.addToPackages("code")

    // Construye el SiteMap
    def sitemap(): SiteMap = SiteMap(
      Menu.i("Home") / "index", // La manera más simple de declarar un menú

      Menu.i("Sometimes") / "sometimes" >> If(displaySometimes_? _,
                                            S ? "Can't view now"), 

      // Un menú con submenús
      Menu.i("Info") / "info" submenus(
        Menu.i("About") / "about" >> Hidden >> LocGroup("bottom"),
        Menu.i("Contact") / "contact",
        Menu.i("Feedback") / "feedback" >> LocGroup("bottom")
      ),
      

      Menu.i("Sitemap") / "sitemap" >> Hidden >> LocGroup("bottom"),

      Menu.i("Dynamic") / "dynamic", // una página con contenido dinámico

      Param.menu,

      Menu.param[Which]("Recurse", "Recurse",
                        {case "one" => Full(First())
                         case "two" => Full(Second())
                         case "both" => Full(Both())
                         case _ => Empty},
                        w => w.toString) / "recurse",
      
      // Más complejo, pues permite que cualquier cosa que se encuentre dentro del directorio
      // /static sea visible
      Menu.i("Static") / "static" / **)

    // Establece el sitemap. Nota si no se quiere control de acceso para
    // cada página, solo comenta la linea a continuación.
    LiftRules.setSiteMapFunc(() => sitemap())

    //Muestra la imágen giratoria cuando una llamada Ajax se inicia
    LiftRules.ajaxStart =
      Full(() => LiftRules.jsArtifacts.show("ajax-loader").cmd)
    
    // Hace que la imágen giratoria desaparezca cuando la llamada Ajax termina
    LiftRules.ajaxEnd =
      Full(() => LiftRules.jsArtifacts.hide("ajax-loader").cmd)

    // Obliga que la solicitud sea UTF-8
    LiftRules.early.append(_.setCharacterEncoding("UTF-8"))

    // Usa HTML5 para el renderizado
    LiftRules.htmlProperties.default.set((r: Req) =>
      new Html5Properties(r.userAgent))    
  }
}
