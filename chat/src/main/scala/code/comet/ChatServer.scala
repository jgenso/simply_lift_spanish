package code
package comet

import net.liftweb._
import http._
import actor._

/**
 * Un Singleton que provee características de chat a todos los clientes.
 * Es un Actor, por lo que es seguro en cuanto a sub procesos
 * solo se procesará un mensaje a la vez.
 */
object ChatServer extends LiftActor with ListenerManager {
  private var msgs = Vector("Welcome") // private state

  /**
   * Cuando se actualiza a los oyentes, ¿Qué mensaje enviamos?
   * Enviamos los mensajes, que es una estructura de datos inmutable,
   * por lo que puede ser compartida por un montón de hilos sin ningún
   * peligro de que ocurra un bloqueo.
   */
  def createUpdate = msgs

  /**
   * procesa los mensajes que son enviados al Actor. En
   * este caso, se busca cadenas que son enviadas al
   * ChatServer.  Se las agrega al Vector de 
   * mensajes, y despues se actualiza todos los oyentes.
   */
  override def lowPriority = {
    case s: String => msgs :+= s; updateListeners()
  }
}
