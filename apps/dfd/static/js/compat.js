/* Compatibilidade com o QtWebEngine usado no build Windows (PyQt5/Qt5).
 * Mantém o editor funcional mesmo quando APIs DOM/Array mais novas não existem.
 */
(() => {
  'use strict';

  if (!Element.prototype.replaceChildren) {
    Element.prototype.replaceChildren = function (...nodes) {
      while (this.firstChild) this.removeChild(this.firstChild);
      nodes.forEach(node => {
        this.appendChild(node instanceof Node ? node : document.createTextNode(String(node)));
      });
    };
  }

  if (!Array.prototype.at) {
    Object.defineProperty(Array.prototype, 'at', {
      configurable: true,
      writable: true,
      value: function (index) {
        const length = this.length >>> 0;
        let i = Number(index) || 0;
        if (i < 0) i += length;
        if (i < 0 || i >= length) return undefined;
        return this[i];
      }
    });
  }
})();
