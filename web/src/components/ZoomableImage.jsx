import { useState, useRef, useEffect } from "react";
import { createPortal } from "react-dom";

const BTN = {
  background: "rgba(255,255,255,.25)", border: "none", color: "#fff",
  fontSize: 20, width: 38, height: 38, borderRadius: 6, cursor: "pointer",
  display: "flex", alignItems: "center", justifyContent: "center",
};

function Lightbox({ src, alt, onClose }) {
  const [zoom, setZoom]   = useState(1);
  const [pos,  setPos]    = useState({ x: 0, y: 0 });
  const zoomRef    = useRef(1);
  const posRef     = useRef({ x: 0, y: 0 });
  const dragging   = useRef(false);
  const dragStart  = useRef({ x: 0, y: 0 });
  const lastTouch  = useRef(null);
  const lastDist   = useRef(null);
  const overlayRef = useRef(null);

  function syncZoom(z) { const v = Math.max(0.5, Math.min(8, z)); zoomRef.current = v; setZoom(v); }
  function syncPos(p)  { posRef.current = p; setPos(p); }
  function reset()     { syncZoom(1); syncPos({ x: 0, y: 0 }); }

  // Escape key
  useEffect(() => {
    const h = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, []);

  // Wheel + touchmove need passive:false to prevent page scroll
  useEffect(() => {
    const el = overlayRef.current;
    if (!el) return;

    const onWheel = (e) => {
      e.preventDefault();
      syncZoom(zoomRef.current + (e.deltaY < 0 ? 0.2 : -0.2));
    };

    const onTouchMove = (e) => {
      e.preventDefault();
      if (e.touches.length === 1 && lastTouch.current) {
        syncPos({
          x: e.touches[0].clientX - lastTouch.current.x,
          y: e.touches[0].clientY - lastTouch.current.y,
        });
      } else if (e.touches.length === 2 && lastDist.current != null) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        syncZoom(zoomRef.current * (dist / lastDist.current));
        lastDist.current = dist;
      }
    };

    el.addEventListener("wheel",     onWheel,     { passive: false });
    el.addEventListener("touchmove", onTouchMove, { passive: false });
    return () => {
      el.removeEventListener("wheel",     onWheel);
      el.removeEventListener("touchmove", onTouchMove);
    };
  }, []);

  function onMouseDown(e) {
    if (e.button !== 0) return;
    e.preventDefault();
    dragging.current = true;
    dragStart.current = { x: e.clientX - posRef.current.x, y: e.clientY - posRef.current.y };
  }
  function onMouseMove(e) {
    if (!dragging.current) return;
    syncPos({ x: e.clientX - dragStart.current.x, y: e.clientY - dragStart.current.y });
  }
  function onMouseUp() { dragging.current = false; }

  function onTouchStart(e) {
    if (e.touches.length === 1) {
      lastTouch.current = {
        x: e.touches[0].clientX - posRef.current.x,
        y: e.touches[0].clientY - posRef.current.y,
      };
      lastDist.current = null;
    } else if (e.touches.length === 2) {
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      lastDist.current = Math.sqrt(dx * dx + dy * dy);
    }
  }
  function onTouchEnd() { lastTouch.current = null; lastDist.current = null; }

  return createPortal(
    <div
      ref={overlayRef}
      onClick={onClose}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
      onMouseLeave={onMouseUp}
      onTouchStart={onTouchStart}
      onTouchEnd={onTouchEnd}
      style={{
        position: "fixed", inset: 0,
        background: "rgba(0,0,0,.92)",
        zIndex: 99999,
        display: "flex", alignItems: "center", justifyContent: "center",
        overflow: "hidden",
      }}
    >
      {/* Close */}
      <button
        onClick={(e) => { e.stopPropagation(); onClose(); }}
        style={{ position: "absolute", top: 16, right: 16, ...BTN, width: 44, height: 44, fontSize: 24, borderRadius: 10 }}
      >✕</button>

      {/* Hint */}
      <div style={{
        position: "absolute", top: 18, left: "50%", transform: "translateX(-50%)",
        color: "rgba(255,255,255,.45)", fontSize: 12, pointerEvents: "none", whiteSpace: "nowrap",
      }}>
        Scroll — zoom · Vilkt — bīdīt · Esc — aizvērt
      </div>

      {/* Controls */}
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          position: "absolute", bottom: 24, left: "50%", transform: "translateX(-50%)",
          display: "flex", gap: 8, alignItems: "center",
          background: "rgba(0,0,0,.6)", borderRadius: 12, padding: "8px 14px",
        }}
      >
        <button onClick={() => syncZoom(zoomRef.current - 0.25)} style={BTN}>−</button>
        <span style={{ color: "#fff", fontSize: 13, minWidth: 48, textAlign: "center" }}>
          {Math.round(zoom * 100)}%
        </span>
        <button onClick={() => syncZoom(zoomRef.current + 0.25)} style={BTN}>+</button>
        <button onClick={reset} style={{ ...BTN, fontSize: 11, width: "auto", padding: "0 12px" }}>1:1</button>
      </div>

      {/* Image */}
      <img
        src={src}
        alt={alt}
        draggable={false}
        onClick={(e) => e.stopPropagation()}
        onMouseDown={onMouseDown}
        style={{
          maxWidth: "90vw", maxHeight: "90vh", objectFit: "contain",
          transform: `translate(${pos.x}px, ${pos.y}px) scale(${zoom})`,
          transformOrigin: "center center",
          cursor: "grab",
          userSelect: "none",
          touchAction: "none",
        }}
      />
    </div>,
    document.body
  );
}

export default function ZoomableImage({ src, alt, style }) {
  const [open, setOpen] = useState(false);

  if (!src) return null;

  return (
    <>
      <img
        src={src}
        alt={alt}
        style={{ ...style, cursor: "zoom-in" }}
        onClick={(e) => { e.stopPropagation(); setOpen(true); }}
      />
      {open && <Lightbox src={src} alt={alt} onClose={() => setOpen(false)} />}
    </>
  );
}
