package code
package snippet

import net.liftweb._
import http._
import js._
import JsCmds._
import JE._

import comet.ChatServer

/**
 * Un snippet que transforma una entrada en una salida... transforma
 * plantillas en contenido dinámico. Las plantillas en Lift pueden invocar
 * snippets y los snippets se resuelven de muchas formas
 * incluyendo "por convención".  El paquete snippet
 * has tiene snippets con nombre y esos snippets pueden ser clases 
 * que son instanciadas cuando se las invoca o pueden ser 
 * objectos, singletons.  Los singletos son utiles si es que
 * no existe manejo explícito de estado en el snippet.
 */
object ChatIn {

  /**
   * El método render en este caso devuelve una función
   * que transforma NodeSeq => NodeSeq.  En este caso,
   * la función transforma, un elemento de entrada de formulario
   * añadiendole un comportamiento. El comportamiento consiste en enviar un mensaje
   * al ChatServer y devolver un JavaScript que limpia el elemento de 
   * entrada.
   */
  def render = SHtml.onSubmit(s => {
    ChatServer ! s
    SetValById("chat_in", "")
  })
}
