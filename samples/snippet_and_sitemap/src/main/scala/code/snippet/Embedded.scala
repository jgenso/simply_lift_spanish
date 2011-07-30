package code
package snippet

import lib._

import net.liftweb._
import http._
import util.Helpers._
import common._
import java.util.Date

/**
 * Un snippet que lista el nombre de la página actual
 */
object Embedded {
  def from = "*" #> S.location.map(_.name)
}

