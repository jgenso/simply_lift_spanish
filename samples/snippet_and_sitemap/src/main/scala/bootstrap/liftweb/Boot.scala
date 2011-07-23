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
 * A class that's instantiated early and run.  It allows the application
 * to modify lift's environment
 */
class Boot {
  /**
   * Calculate if the page should be displayed.
   * In this case, it will be visible every other minute
   */
  def displaySometimes_? : Boolean = 
    (millis / 1000L / 60L) % 2 == 0

  def boot {
    // where to search snippet
    LiftRules.addToPackages("code")

    // Build SiteMap
    def sitemap(): SiteMap = SiteMap(
      Menu.i("Home") / "index", // the simple way to declare a menu

      Menu.i("Sometimes") / "sometimes" >> If(displaySometimes_? _,
                                            S ? "Can't view now"), 

      // A menu with submenus
      Menu.i("Info") / "info" submenus(
        Menu.i("About") / "about" >> Hidden >> LocGroup("bottom"),
        Menu.i("Contact") / "contact",
        Menu.i("Feedback") / "feedback" >> LocGroup("bottom")
      ),
      

      Menu.i("Sitemap") / "sitemap" >> Hidden >> LocGroup("bottom"),

      Menu.i("Dynamic") / "dynamic", // a page with dynamic content

      Param.menu,

      Menu.param[Which]("Recurse", "Recurse",
                        {case "one" => Full(First())
                         case "two" => Full(Second())
                         case "both" => Full(Both())
                         case _ => Empty},
                        w => w.toString) / "recurse",
      
      // more complex because this menu allows anything in the
      // /static path to be visible
      Menu.i("Static") / "static" / **)

    // set the sitemap.  Note if you don't want access control for
    // each page, just comment this line out.
    LiftRules.setSiteMapFunc(() => sitemap())

    //Show the spinny image when an Ajax call starts
    LiftRules.ajaxStart =
      Full(() => LiftRules.jsArtifacts.show("ajax-loader").cmd)
    
    // Make the spinny image go away when it ends
    LiftRules.ajaxEnd =
      Full(() => LiftRules.jsArtifacts.hide("ajax-loader").cmd)

    // Force the request to be UTF-8
    LiftRules.early.append(_.setCharacterEncoding("UTF-8"))

    // Use HTML5 for rendering
    LiftRules.htmlProperties.default.set((r: Req) =>
      new Html5Properties(r.userAgent))    
  }
}
