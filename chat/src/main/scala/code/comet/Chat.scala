package code
package comet

import net.liftweb._
import http._
import util._
import Helpers._

/**
 * El estado real de la pantalla será representado por mediante
 * este componente. Cuando el componente cambia en el servidor
 * los cambios son reflejados automáticamente en el navegador.
 */
class Chat extends CometActor with CometListener {
  private var msgs: Vector[String] = Vector() // estado privado

  /**
   * Cuando se instancia el componente, se registra como
   * un oyente en el ChatServer
   */
  def registerWith = ChatServer

  /**
   * El CometActor es un Actor, por lo que procesa mensajes.
   * En este caso, se está oyendo por un Vector[String],
   * y cuando se obtiene uno, se actualiza el estado privado
   * y se re-renderiza el componente.  reRender() hará
   * que los cambios sean enviados al navegador.
   */
  override def lowPriority = {
    case v: Vector[String] => msgs = v; reRender()
  }

  /**
   * Se pone los mensajes en los elementos li y se limpia
   * cualquier elemento que tenga la clase clearable.
   */
  def render = "li *" #> msgs & ClearClearable
}
