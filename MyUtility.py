#import config module for environmental variability
from matplotlib.pyplot import gray
import config
import numpy as np
#import my utility class and function
import MyUtility


#tkinter import
import tkinter as tk
import pandas as pd
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from tkinter.messagebox import showinfo
from tkinter.ttk import Separator, Style

import math

#common variable
workDict = {}
workDict["master_protein_separator"] = "; "

import tkinter as tk
import pandas as pd
import numpy as np
from typing import List, Optional


class VirtualCheckboxList(tk.Frame):
    """
    A high-performance, virtualized checkbox list for very large and dynamic datasets.

    Core idea:
      - The Canvas DOES NOT scroll vertically. The vertical scrollbar acts as a logical controller:
        it adjusts `first_visible_index` and we rebind a small set of physical Checkbuttons.
      - The vertical scrollbar's thumb is updated to reflect (first_visible_index, total_rows, viewport_rows).
      - Horizontal scrolling remains native on the Canvas (Shift+Wheel / Linux buttons).

    Public API:
      - insertCheckbox(items: list[str], itemsDescription: Optional[list[str]] = None, checks: Optional[list[int]] = None)
      - removeAllCheckbox()
      - selectedItems() -> list[str]
      - select_all(), deselect_all()
      - select_filtered(), deselect_filtered()
      - scroll_to_top()

      - set_size(width: int | None, height: int | None)
      - set_row_height(row_height: int)
      - set_viewport_rows(viewport_rows: int)

    Notes:
      - Internally, items are stored in a pandas DataFrame with columns: "code", "description", "description_lc".
      - `itemsViewed` is a whitelist of codes that can appear in the current view (e.g., after external changes).
      - `sel_state` is a list[int] (0/1) aligned by index with the DataFrame rows.
      - `filtered_indices` maps the logical slice currently visible to dataframe indices.
    """

    def __init__(
        self,
        master=None,
        search: bool = False,
        select: bool = False,
        callback_on_change_set_checks=None,
        row_height: int = 26,
        viewport_rows: int = 40,
        **kw
    ):
        """
        Build the widget layout and initialize state.

        Args:
            master: Tk parent.
            search: If True, shows a search Entry that filters the list by description.
            select: If True, shows Select/Deselect All and Select/Deselect Filtered buttons.
            callback_on_change_set_checks: Optional callable fired when selection changes.
            row_height: Estimated pixel height per row (used only as initial hint; now we measure the real pitch).
            viewport_rows: How many physical Checkbuttons to keep alive and reuse.
            **kw: Forwarded options; recognizes 'width' and 'height' for the Canvas.
        """
        super().__init__(master, **kw)

        # --- Tunables ---
        # Keep kw overrides to allow both ctor args and **kw usage.
        self.row_height = kw.get("row_height", row_height)
        self.viewport_rows = kw.get("viewport_rows", viewport_rows)

        # --- Options ---
        self.search = search
        self.select = select
        self._callback_on_change_set_checks = callback_on_change_set_checks

        # --- Data model ---
        self.items = pd.DataFrame(columns=["code", "description", "description_lc"])
        self.itemsViewed: List[str] = []   # whitelist of codes allowed to appear
        self.sel_state: List[int] = []     # 0/1 flags aligned with self.items
        self.filtered_indices: List[int] = []  # indices into self.items after filter

        # --- Viewport state ---
        self.visible_checks: List[tk.Checkbutton] = []  # physical Checkbuttons (reused)
        self.visible_vars: List[tk.IntVar] = []         # IntVars for those Checkbuttons
        self.first_visible_index: int = 0               # index in filtered_indices of the top logical row

        # --- Mouse wheel flags ---
        self._v_wheel_enabled = False
        self._h_wheel_enabled = False

        # --- Layout ---
        row = 0

        # Search bar (optional)
        if self.search:
            self.frame_search = tk.Frame(self)
            self.frame_search.grid(row=row, column=0, columnspan=2, sticky="nsew")
            tk.Label(self.frame_search, text="Search").grid(row=0, column=0, padx=6, pady=6, sticky="w")
            self.ntr_search_var = tk.StringVar(value="")
            self.ntr_search = tk.Entry(self.frame_search, textvariable=self.ntr_search_var, width=20)
            self.ntr_search.grid(row=0, column=1, sticky="ew", padx=(0, 6), pady=6)
            self.frame_search.columnconfigure(1, weight=1)
            # Refilter live on every change
            self.ntr_search_var.trace_add("write", self._on_search_change)
            row += 1

        # Select/Deselect all controls (optional)
        if self.select:
            self.frame_select_all = tk.Frame(self)
            self.frame_select_all.grid(row=row, column=0, columnspan=2, sticky="nsew")
            self.frame_select_all.columnconfigure(0, weight=1, uniform="half")
            self.frame_select_all.columnconfigure(1, weight=1, uniform="half")
            tk.Button(self.frame_select_all, text="Select all", command=self.selectAllItems)\
                .grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
            tk.Button(self.frame_select_all, text="Deselect all", command=self.deselectAllItems)\
                .grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
            row += 1

        # Select/Deselect matches controls (optional)
        if self.search and self.select:
            self.frame_select_filtered = tk.Frame(self)
            self.frame_select_filtered.grid(row=row, column=0, columnspan=2, sticky="nsew")
            self.frame_select_filtered.columnconfigure(0, weight=1, uniform="half")
            self.frame_select_filtered.columnconfigure(1, weight=1, uniform="half")
            tk.Button(self.frame_select_filtered, text="Select matches", command=self.selectFiltered)\
                .grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
            tk.Button(self.frame_select_filtered, text="Deselect matches", command=self.deselectFiltered)\
                .grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
            row += 1

        # Canvas + scrollbars (scrollbars always visible)
        width = kw.get("width", 300)
        height = kw.get("height", 300)
        self.canvas = tk.Canvas(self, width=width, height=height, bd=0, highlightthickness=0)

        # IMPORTANT: vertical scrollbar uses our handler; we DO NOT call canvas.yview
        self.yscroll = tk.Scrollbar(self, orient="vertical", command=self._on_yscrollbar)

        # Horizontal remains native (Canvas manages xview)
        self.xscroll = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)

        # Inner frame with a fixed small number of physical rows
        self.inner = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        # Keep scrollbars visible in the grid
        self.canvas.grid(row=row, column=0, sticky="nsew")
        self.yscroll.grid(row=row, column=1, sticky="ns")
        row += 1
        self.xscroll.grid(row=row, column=0, columnspan=2, sticky="ew")

        # Expand canvas row
        self.rowconfigure(row - 1, weight=1)
        self.columnconfigure(0, weight=1)

        # Linkage: vertical yscrollcommand is a dummy proxy (we compute thumb ourselves)
        # Horizontal xscrollcommand is native to keep horizontal scroll working
        self.canvas.configure(yscrollcommand=self._on_canvas_yview_proxy, xscrollcommand=self.xscroll.set)

        # Build the physical rows once
        self._build_viewport_rows()

        # Track geometry: only needed for horizontal scrollregion
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_resized)

        # Mouse wheel: vertical/horizontal (enable/disable via flags)
        self.canvas.bind("<Enter>", self._on_canvas_enter)
        self.canvas.bind("<Leave>", self._on_canvas_leave)

        # Windows/macOS horizontal with Shift
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)

        # Start with wheels disabled; will be enabled when needed
        self._enable_vertical_wheel(False)
        self._enable_horizontal_wheel(False)

        # Initialize empty model (no items yet)
        self._apply_filter("")

    # =======================
    # Public API
    # =======================
    def insertItems(self, items: List[str], itemsDescription: Optional[List[str]] = None, checks: Optional[List[int]] = None):
        """
        Replace items; apply current filter (if any).
        If `checks` is not provided, all items are selected by default.
        """
        self.itemsViewed = list(items)

        # Build dataframe and a lowercase column for faster case-insensitive search
        if itemsDescription is not None:
            if len(items) != len(itemsDescription):
                raise ValueError(
                    "The two lists must have the same length: "
                    f"{len(items)=} vs {len(itemsDescription)=}"
                )
            df = pd.DataFrame({"code": items, "description": itemsDescription})
        else:
            df = pd.DataFrame({"code": items, "description": items})

        df["description_lc"] = df["description"].astype(str).str.lower()
        self.items = df

        # Validate checks (if provided) and normalize to 0/1 ints
        if checks is not None:
            if len(checks) != len(self.items):
                raise ValueError(
                    f"`checks` length ({len(checks)}) must match items length ({len(self.items)})"
                )
            self.sel_state = checks 
        else:
            self.sel_state = [1] * len(self.items)

        query = self.ntr_search_var.get() if self.search else ""
        self._apply_filter(query)

    def replaceItemsDescription(self, itemsDescription: List[str]):
        """
        Replace itemsDescription; apply current filter (if any).
        If `checks` is not provided, all items are selected by default.
        """
        items = self.items["code"].tolist()

        # Build dataframe and a lowercase column for faster case-insensitive search
        if itemsDescription is not None:
            if len(items) != len(itemsDescription):
                raise ValueError(
                    "The two lists must have the same length: "
                    f"{len(items)=} vs {len(itemsDescription)=}"
                )
            df = pd.DataFrame({"code": items, "description": itemsDescription})
        else:
            df = pd.DataFrame({"code": items, "description": items})

        df["description_lc"] = df["description"].astype(str).str.lower()
        self.items = df

        query = self.ntr_search_var.get() if self.search else ""
        self._apply_filter(query)

    def changeItemsViewed(self, itemsViewed: List[str]):
        """Replace the whitelist of codes that can appear in the view and re-apply the current filter."""
        self.itemsViewed = list(itemsViewed)
        query = self.ntr_search_var.get() if self.search else ""
        self._apply_filter(query)

    def removeAllItems(self):
        """
        Clear ALL items and selections and blank the viewport rows.
        Physical Checkbutton widgets are kept alive for performance (virtualized list).
        """
        # Keep data model consistent: always a DataFrame with the expected columns
        self.items = pd.DataFrame(columns=["code", "description", "description_lc"])
        self.itemsViewed = []
        self.sel_state = []
        self.filtered_indices = []
        self.first_visible_index = 0

        # Blank/disable all physical rows
        for chk, var in zip(self.visible_checks, self.visible_vars):
            chk.configure(text="", state="disabled")
            var.set(0)

        # Reset search entry (if any)
        if getattr(self, "search", False):
            try:
                self.ntr_search_var.set("")
            except Exception:
                pass

        # Update bars/thumb and behavior (keep scrollbars visible but inert)
        #print("removeAllItems")
        self._update_scrollbar_thumb()
        self._refresh_scrollbars_visibility_and_behavior()

    def selectedItems(self) -> List[str]:
        """Return the 'code' values of globally selected items."""
        mask = np.array(self.sel_state, dtype=bool)
        if len(mask) != len(self.items):
            raise ValueError(f"sel_state length ({len(mask)}) != items length ({len(self.items)})")
        return self.items.iloc[mask]["code"].astype(str).tolist()

    def selectedItemsDescription(self) -> List[str]:
        """Return the 'description' values of globally selected items."""
        mask = np.array(self.sel_state, dtype=bool)
        if len(mask) != len(self.items):
            raise ValueError(f"sel_state length ({len(mask)}) != items length ({len(self.items)})")
        return self.items.iloc[mask]["description"].astype(str).tolist()

    def selectAllItems(self):
        """Select all items globally; reset filter if search is enabled."""
        for idx in range(len(self.items)):
            self.sel_state[idx] = 1
        if self.search:
            self.ntr_search_var.set("")
        self._apply_filter("")
        if self._callback_on_change_set_checks:
            self._callback_on_change_set_checks()

    def deselectAllItems(self):
        """Deselect all items globally; reset filter if search is enabled."""
        for idx in range(len(self.items)):
            self.sel_state[idx] = 0
        if self.search:
            self.ntr_search_var.set("")
        self._apply_filter("")
        if self._callback_on_change_set_checks:
            self._callback_on_change_set_checks()

    def selectFiltered(self):
        """Select only items currently matching the filter."""
        for idx in self.filtered_indices:
            self.sel_state[idx] = 1
        self._refresh_viewport_rows()
        if self._callback_on_change_set_checks:
            self._callback_on_change_set_checks()

    def deselectFiltered(self):
        """Deselect only items currently matching the filter."""
        for idx in self.filtered_indices:
            self.sel_state[idx] = 0
        self._refresh_viewport_rows()
        if self._callback_on_change_set_checks:
            self._callback_on_change_set_checks()

    def scrollToTop(self):
        """Jump to the top (first_visible_index = 0)."""
        self.first_visible_index = 0
        self._refresh_viewport_rows()
        #print("scrollToTop")
        self._update_scrollbar_thumb()

    def filterDataframe(self, dataframe: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Return a *new* DataFrame filtered according to the current selection model.
        """
        if column not in dataframe.columns:
            return dataframe.copy()
        
        if not isinstance(self.items, pd.DataFrame) or self.items.empty:
            return dataframe.copy()
        
        mask_sel = np.array(self.sel_state, dtype=bool)
        if len(mask_sel) != len(self.items):
            raise ValueError(f"sel_state length ({len(mask_sel)}) != items length ({len(self.items)})")
        
        selected_codes = set(self.items.loc[mask_sel, "code"].astype(str).tolist())
        
        empty_selected = "Empty" in selected_codes
        if empty_selected:
            selected_codes.discard("Empty")
        
        col_str = dataframe[column].astype("string")
        base_keep = col_str.isin(selected_codes)
        
        if empty_selected:
            keep = base_keep | dataframe[column].isna()
        else:
            keep = base_keep & dataframe[column].notna()
        
        return dataframe.loc[keep].copy()

    def destroy(self):
        """Release global wheel capture before destroying to avoid leaving cross-widget bindings behind."""
        try:
            self.canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass
        super().destroy()

    # =======================
    # Internal: viewport rows
    # =======================
    def _build_viewport_rows(self):
        """
        Create a fixed number of physical Checkbuttons to be reused.
        Also adapt the inner window height to the *measured* row pitch.
        """
        for r in range(self.viewport_rows):
            var = tk.IntVar(value=0)
            chk = tk.Checkbutton(
                self.inner,
                text="",
                anchor="w",
                variable=var,
                onvalue=1,
                offvalue=0,
                command=lambda row=r: self._on_row_toggled(row)
            )
            chk.grid(row=r, column=0, sticky="w", padx=5, pady=5)
            self.visible_checks.append(chk)
            self.visible_vars.append(var)

        # NEW: set inner height based on measured row pitch to avoid logical/physical mismatch
        self._update_inner_height_to_pitch()

        # Initial thumb update
        #print("_build_viewport_rows")
        self._update_scrollbar_thumb()

    def _refresh_viewport_rows(self):
        """
        Bind physical rows to the current logical slice [first_visible_index : first+viewport].
        Rows outside the range are disabled and cleared to avoid stray focus/interaction.
        """
        total = len(self.filtered_indices)
        start = max(0, min(self.first_visible_index, self._max_first_index()))
        end = min(total, start + self.viewport_rows)

        for i in range(self.viewport_rows):
            row_idx = start + i
            chk = self.visible_checks[i]
            var = self.visible_vars[i]

            if row_idx < end:
                item_idx = self.filtered_indices[row_idx]
                chk.configure(text=self.items.loc[item_idx, "description"])
                var.set(self.sel_state[item_idx])
                chk.configure(state="normal")
            else:
                chk.configure(text="")
                var.set(0)
                chk.configure(state="disabled")

        # Adjust behavior of scrollbars/wheels (bars remain visible)
        self._refresh_scrollbars_visibility_and_behavior()

    def _on_row_toggled(self, physical_row: int):
        """
        Map a physical (visible) row back to the logical item and update selection state.
        Fires the external callback (if provided).
        """
        total = len(self.filtered_indices)
        row_idx = self.first_visible_index + physical_row
        if 0 <= row_idx < total:
            item_idx = self.filtered_indices[row_idx]
            self.sel_state[item_idx] = 1 if self.visible_vars[physical_row].get() == 1 else 0
            if self._callback_on_change_set_checks:
                self._callback_on_change_set_checks()

    # =======================
    # Filtering
    # =======================
    def _on_search_change(self, *_):
        """Search Entry callback: apply filter on each change."""
        self._apply_filter(self.ntr_search_var.get())

    def _apply_filter(self, text: str):
        """
        Compute filtered indices and reset viewport to top.
        Filtering is case-insensitive and restricted to `itemsViewed` whitelist.
        """
        needle = (text or "").strip().lower()

        if not self.items.empty:
            if needle:
                mask = (
                    self.items["description_lc"].str.contains(needle, na=False)
                    & self.items["code"].isin(self.itemsViewed)
                )
            else:
                mask = self.items["code"].isin(self.itemsViewed)

            self.filtered_indices = self.items.index[mask].to_list()
        else:
            self.filtered_indices = []

        # Reset viewport and update rows
        self.first_visible_index = 0
        self._refresh_viewport_rows()
        #print("_apply_filter")
        self._update_scrollbar_thumb()

    # =======================
    # Scrollbars (logic only)
    # =======================
    def _max_first_index(self) -> int:
        """Maximum allowed first_visible_index so that the last page is full (based on effective visible rows)."""
        total = len(self.filtered_indices)
        eff_rows = self._effective_rows_in_viewport()
        return max(0, total - eff_rows)

    def _set_scrollbar_thumb_safely(self, lo: float, hi: float):
        """
        Update scrollbar thumb without triggering recursive callbacks.
        """
        # Detach callback
        self.yscroll.configure(command=lambda *a, **k: None)
        self.yscroll.set(lo, hi)
        # Reattach callback
        self.yscroll.configure(command=self._on_yscrollbar)

    def _update_scrollbar_thumb(self):
        total = len(self.filtered_indices)
        if total == 0:
            self._set_scrollbar_thumb_safely(0.0, 1.0)
            return
    
        first = max(0, min(self.first_visible_index, self._max_first_index()))
        eff_rows = self._effective_rows_in_viewport()
        vis = min(eff_rows, total)
    
        lo = first / total
        hi = min(1.0, (first + vis) / total)
    
        self._set_scrollbar_thumb_safely(lo, hi)

    def _on_yscrollbar(self, *args):
        """
        Vertical scrollbar moved by the user. We DO NOT call canvas.yview.
        We only map the scrollbar commands to first_visible_index and refresh rows.
        """
        if not args:
            return
        kind = args[0]
        max_first = self._max_first_index()

        if kind == "moveto":
            frac = float(args[1])
            new_first = int(frac * max_first)
            first_visible_index = max(0, min(new_first, max_first))
            self.first_visible_index = first_visible_index
        elif kind == "scroll":
            n = int(args[1])
            what = args[2]
            if what == "units":
                self.first_visible_index = max(0, min(self.first_visible_index + n, max_first))
            elif what == "pages":
                eff_rows = self._effective_rows_in_viewport()
                self.first_visible_index = max(
                    0, min(self.first_visible_index + n * eff_rows, max_first)
                )

        self._refresh_viewport_rows()
        self._update_scrollbar_thumb()

    def _on_canvas_yview_proxy(self, *args):
        """Dummy proxy to satisfy Canvas 'yscrollcommand' signature."""
        pass

    # =======================
    # Mouse wheel
    # =======================
    def _enable_vertical_wheel(self, enable: bool):
        """Enable/disable capturing global vertical wheel while pointer is over the canvas."""
        self._v_wheel_enabled = bool(enable)

    def _enable_horizontal_wheel(self, enable: bool):
        """Enable/disable horizontal wheel behavior (Shift+Wheel on Windows/macOS)."""
        self._h_wheel_enabled = bool(enable)

    def _on_canvas_enter(self, _event):
        """Capture global MouseWheel only if vertical scrolling is actually needed."""
        if self._v_wheel_enabled:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        else:
            try:
                self.canvas.unbind_all("<MouseWheel>")
            except Exception:
                pass

    def _on_canvas_leave(self, _event):
        """Release global wheel capture when leaving the canvas."""
        try:
            self.canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass

    # Windows/macOS: vertical wheel
    def _on_mousewheel(self, event):
        if not self._v_wheel_enabled:
            return
        delta = int(-1 * (event.delta / 120)) if event.delta else 0
        if delta:
            max_first = self._max_first_index()
            self.first_visible_index = max(0, min(self.first_visible_index + delta, max_first))
            self._refresh_viewport_rows()
            self._update_scrollbar_thumb()

    # Windows/macOS: Shift + wheel = horizontal scroll
    def _on_shift_mousewheel(self, event):
        if not self._h_wheel_enabled:
            return
        delta = int(-1 * (event.delta / 120)) if event.delta else 0
        if delta:
            self.canvas.xview_scroll(delta, "units")

    # =======================
    # Horizontal scrollregion
    # =======================
    def _on_inner_configure(self, _event):
        """
        Update the Canvas scrollregion mainly to reflect horizontal size.
        Vertical scrollregion is irrelevant because we never scroll the Canvas vertically.
        """
        bbox = self.canvas.bbox("all") or (0, 0, 0, 0)
        self.canvas.configure(scrollregion=bbox)

    def _on_canvas_resized(self, _event):
        """
        On Canvas resize, refresh rows, thumb and keep inner height aligned to the measured pitch.
        """
        self._update_inner_height_to_pitch()
        self._refresh_viewport_rows()
        self._update_scrollbar_thumb()

    # =======================
    # Behavior toggling
    # =======================
    def _refresh_scrollbars_visibility_and_behavior(self):
        """
        Keep scrollbars visible; make them inert if not needed.
        Vertical need is based on (total_rows > effective_rows_in_viewport).
        Horizontal need is based on content width vs visible width.
        """
        total = len(self.filtered_indices)
        eff_rows = self._effective_rows_in_viewport()
        need_v = total > eff_rows
        self._enable_vertical_wheel(need_v)

        # Horizontal need: compare bbox width to visible width
        bbox = self.canvas.bbox("all") or (0, 0, 0, 0)
        try:
            visible_w = self.canvas.winfo_width()
        except Exception:
            visible_w = int(self.canvas.cget("width"))
        content_w = bbox[2] - bbox[0]
        need_h = content_w > visible_w
        self._enable_horizontal_wheel(need_h)

        # Vertical: keep bar visible; detach commands if inert (no-op behavior)
        if need_v:
            self.yscroll.configure(command=self._on_yscrollbar)
        else:
            self.yscroll.configure(command=lambda *a, **k: None)

        # Horizontal: native Canvas xview; detach if inert
        if need_h:
            self.canvas.configure(xscrollcommand=self.xscroll.set)
            self.xscroll.configure(command=self.canvas.xview)
        else:
            self.canvas.configure(xscrollcommand=lambda *a, **k: None)
            self.xscroll.configure(command=lambda *a, **k: None)

    # =======================
    # Size & tuning
    # =======================
    def set_size(self, width: Optional[int] = None, height: Optional[int] = None):
        """
        Update canvas size and realign the UI.
        If height changes, align inner window height to measured pitch * viewport_rows.
        """
        if width is not None:
            self.canvas.configure(width=width)
        if height is not None:
            self.canvas.configure(height=height)
            self._update_inner_height_to_pitch()
        self._refresh_viewport_rows()
        self._update_scrollbar_thumb()

    def set_row_height(self, row_height: int):
        """
        Change the logical row height hint and update the inner window using measured pitch.
        """
        self.row_height = int(row_height)
        self._update_inner_height_to_pitch()
        self._refresh_viewport_rows()
        self._update_scrollbar_thumb()

    def set_viewport_rows(self, viewport_rows: int):
        """
        Rebuild the physical widgets to use exactly `viewport_rows` visible rows (physical).
        """
        viewport_rows = int(viewport_rows)
        if viewport_rows <= 0 or viewport_rows == self.viewport_rows:
            return

        # Destroy current physical rows
        for chk in self.visible_checks:
            chk.destroy()
        self.visible_checks.clear()
        self.visible_vars.clear()

        self.viewport_rows = viewport_rows
        self._build_viewport_rows()
        self._refresh_viewport_rows()
        self._update_scrollbar_thumb()

    # =======================
    # Measured-pitch helpers (NEW)
    # =======================
    def _measure_row_pitch(self) -> int:
        """
        Return the effective vertical pitch (distance) between two consecutive rows, in pixels,
        including widget height and vertical padding.
        """
        try:
            self.update_idletasks()
        except Exception:
            pass

        # If we don't have at least two rows yet, estimate using the first row reqheight + grid pady*2 (pady=5)
        if len(self.visible_checks) < 2:
            h = self.visible_checks[0].winfo_reqheight() if self.visible_checks else self.row_height
            return int(h + 10)  # 2 * 5

        y0 = self.visible_checks[0].winfo_rooty()
        y1 = self.visible_checks[1].winfo_rooty()
        pitch = max(1, int(y1 - y0))
        return pitch

    def _effective_rows_in_viewport(self) -> int:
        """
        Compute how many full rows actually fit in the current Canvas height.
        """
        try:
            self.update_idletasks()
        except Exception:
            pass

        try:
            visible_h = self.canvas.winfo_height()
            if visible_h <= 1:
                visible_h = int(self.canvas.cget("height"))
        except Exception:
            visible_h = int(self.canvas.cget("height"))

        pitch = self._measure_row_pitch()
        eff = max(1, visible_h // pitch)
        # Never exceed the number of physical rows we keep alive
        eff = min(eff, self.viewport_rows) if self.viewport_rows > 0 else eff
        return eff

    def _update_inner_height_to_pitch(self):
        """
        Keep the inner window height aligned to `viewport_rows * measured_pitch`.
        This avoids logical/physical row count mismatch in the viewport.
        """
        pitch = self._measure_row_pitch()
        self.canvas.itemconfigure(self.canvas_window, height=self.viewport_rows * pitch)

    # =======================
    # Backward-compatibility aliases (as per the docstring names)
    # =======================
    def insertCheckbox(self, items: List[str], itemsDescription: Optional[List[str]] = None, checks: Optional[List[int]] = None):
        return self.insertItems(items, itemsDescription, checks)

    def removeAllCheckbox(self):
        return self.removeAllItems()

    def select_all(self):
        return self.selectAllItems()

    def deselect_all(self):
        return self.deselectAllItems()

    def select_filtered(self):
        return self.selectFiltered()

    def deselect_filtered(self):
        return self.deselectFiltered()

    def scroll_to_top(self):
        return self.scrollToTop()









class AggregatorVirtualCheckboxList(tk.Frame):
    def __init__(
                    self, 
                    master=None, 
                    search=False, 
                    select=False, 
                    with_lineage = False, 
                    label_normal = "Normal",
                    label_lineage = "Lineage",
                    width=200, 
                    height=360, 
                    row_height=26, 
                    viewport_rows=40, 
                    **kw
                    ):

        super().__init__(master, **kw)

        # Stores available dataframe columns
        self.columns = []

        # One list of values for each column
        self.aggregatorLists = []

        # Checkbox state associated with each value
        self.aggregatorChecks = []

        self.with_lineage = with_lineage

        # Create radio buttons to switch between normal and lineage view
        if(self.with_lineage):
            self.rbd_frame = Frame(self, width=20, height=20)
            self.rbd_frame.grid(row=0, column=0)
            self.rdb_var = StringVar(value='normal')
            self.rdb_normal = tk.Radiobutton(self.rbd_frame, text=label_normal, width=10, variable=self.rdb_var, value='normal', command=self._on_change_radio_buttons)
            self.rdb_normal.grid(row=0, column=0)
            self.rdb_normal.config( font = config.font_checkbox )
            self.rdb_lineage = tk.Radiobutton(self.rbd_frame, text=label_lineage, width=10, variable=self.rdb_var, value='lineage', command=self._on_change_radio_buttons)
            self.rdb_lineage.grid(row=0, column=1)
            self.rdb_lineage.config( font = config.font_checkbox )
        else:
            self.rdb_var = StringVar(value='normal')

        # Dropdown used to select the active column
        self.idx_opt_columns = 0
        self.columns = [("")]
        self.opt_columns_var = StringVar(value="")
        self.opt_columns = tk.OptionMenu(self, self.opt_columns_var, *self.columns, command=self._on_change_opt_columns)
        self.opt_columns.configure(width=30)
        self.opt_columns.config(font = config.font_checkbox)
        self.opt_columns.grid(row=1, column=0)

        # Virtualized checkbox list used to display values
        self.scl_check_aggregator = MyUtility.VirtualCheckboxList(
                                                      self, 
                                                      width=width,
                                                      height=height,
                                                      bg="grey", 
                                                      padx=1, 
                                                      pady=1, 
                                                      select=select,
                                                      search=search,
                                                      row_height=row_height,
                                                      viewport_rows=viewport_rows
                                                      )
        self.scl_check_aggregator.grid(row=2, column=0)

    def _on_change_radio_buttons(self):
        # Refresh current column when display mode changes
        selected_value = self.columns[self.idx_opt_columns]
        self._on_change_opt_columns(selected_value)

    def _on_change_opt_columns(self, selected_value):
        # Save selected column index
        self.idx_opt_columns = self.columns.index(selected_value)

        if(len(self.aggregatorLists)>0):
            self.scl_check_aggregator.grid()

            # Sort by lineage description
            if(self.rdb_var.get()=="lineage" and self.with_lineage==True):
                order = sorted(zip(self.aggregatorListDescriptions[self.idx_opt_columns], self.aggregatorLists[self.idx_opt_columns], self.aggregatorChecks[self.idx_opt_columns]))
                self.aggregatorListDescriptions[self.idx_opt_columns], self.aggregatorLists[self.idx_opt_columns], self.aggregatorChecks[self.idx_opt_columns] = zip(*order)

                self.aggregatorChecks[self.idx_opt_columns] = list(self.aggregatorChecks[self.idx_opt_columns])

                aggregatorList = self.aggregatorListDescriptions[self.idx_opt_columns]
                aggregatorListDescription = self.aggregatorListDescriptions[self.idx_opt_columns]

            # Sort by original value
            else:
                order = sorted(zip(self.aggregatorLists[self.idx_opt_columns], self.aggregatorListDescriptions[self.idx_opt_columns], self.aggregatorChecks[self.idx_opt_columns]))
                self.aggregatorLists[self.idx_opt_columns], self.aggregatorListDescriptions[self.idx_opt_columns], self.aggregatorChecks[self.idx_opt_columns] = zip(*order)

                self.aggregatorChecks[self.idx_opt_columns] = list(self.aggregatorChecks[self.idx_opt_columns])

                aggregatorList = self.aggregatorLists[self.idx_opt_columns]
                aggregatorListDescription = self.aggregatorLists[self.idx_opt_columns]

            aggregatorCheck = self.aggregatorChecks[self.idx_opt_columns]

            self.scl_check_aggregator.insertItems(items=aggregatorList, checks=aggregatorCheck, itemsDescription=aggregatorListDescription)
            self.scl_check_aggregator.scrollToTop()

    def _update_optionmenu(self, widget_optionmenu, var, new_list, callback, default_value=None, preserve_if_possible=True):
        """
        Rebuild the OptionMenu content while preserving
        the current selection whenever possible.
        """

        menu = widget_optionmenu["menu"]
        menu.delete(0, "end")  # empty menu

        # choose the value after update
        curret_value = var.get()
        if preserve_if_possible and curret_value in new_list:
            new_value = curret_value
        elif default_value in new_list:
            new_value = default_value
        elif new_list is not None:
            new_value = new_list[0]
        else:
            new_value = ""  # null value

        # rebuild menu
        for item in new_list:
            menu.add_command(label=item, command=lambda v=item: (var.set(v), callback(v)))

        var.set(new_value)

    def setDataframe(self, dataframe, exclude = ["peptide"]):
        self.dataframe = dataframe.drop(exclude, axis=1)
        self.columns = self.dataframe.columns.tolist()
        self.aggregatorLists = []
        self.aggregatorListDescriptions = []
        self.aggregatorChecks = []

        if(self.with_lineage):
            columns_no_lineage = [x for x in self.columns if "lca" in x.lower()]
            columns_lineage = [x for x in self.columns if x not in columns_no_lineage]
        else:
            columns_no_lineage = self.columns

        for column in columns_no_lineage:
            aggregatorList = MyUtility.create_unique_list(self.dataframe, column)
            self.aggregatorLists.append(aggregatorList)

            self.aggregatorListDescriptions.append(aggregatorList)

            aggregatorCheck = [1] * len(aggregatorList)
            self.aggregatorChecks.append(aggregatorCheck)

        if(self.with_lineage):
            index = -1
            for column in columns_lineage:
                index = index + 1
    
                aggregatorList = MyUtility.create_unique_list(self.dataframe, column)
    
                if(self.with_lineage == True):
                    aggregatorListDescriptions = self._get_lineage_list(columns_lineage, aggregatorList, index)

                    order = sorted(zip(aggregatorListDescriptions, aggregatorList))
                    aggregatorListDescriptions, aggregatorList = zip(*order)
                else:
                    aggregatorListDescriptions = aggregatorList
    
                aggregatorCheck = [1] * len(aggregatorList)

                self.aggregatorLists.append(aggregatorList)
                self.aggregatorListDescriptions.append(aggregatorListDescriptions)
                self.aggregatorChecks.append(aggregatorCheck)

        self._update_optionmenu(self.opt_columns, self.opt_columns_var, self.columns, self._on_change_opt_columns)
        self._on_change_opt_columns(self.columns[0])

    def _get_lineage_list(self, columns_lineage, aggregatorList, index):
        aggregatorListNew = []
        if(index == 0):
            aggregatorListNew = aggregatorList
        else:
            for i in range(len(aggregatorList)):
                valore = ""

                ris = self.dataframe[self.dataframe[columns_lineage[index]] == aggregatorList[i]]
                ris = ris[columns_lineage]
                if not ris.empty:
                    riga = ris.iloc[0]
                    for j in range(index):
                        try:
                            valore = valore + riga[j] + "|"
                        except:
                            pass

                valore = valore + aggregatorList[i]
                aggregatorListNew.append(valore)

        return aggregatorListNew

    def filterDataframe(self, dataframe):
        if(len(self.columns)>0):
            j = 0
            for column in self.columns:
                i = 0
                for item in self.aggregatorLists[j]:
                    if(self.aggregatorChecks[j][i] == 0):
                        if(item == "Empty"):
                            dataframe = dataframe.dropna(subset=[column])
                        else:
                            #print(item.cget("text"))
                            dataframe.drop(dataframe.index[dataframe[column] == item], inplace=True)
                    i = i + 1
                j = j + 1

        return dataframe





class Separator(tk.Frame):
    """
    Simple visual separator.
    Can be horizontal or vertical.
    """

    def __init__(self, master=None, orient='horizontal', **kwargs):
        super().__init__(master, **kwargs)
        if orient == 'horizontal':
            self.columnconfigure(0, weight=1)
            self.rowconfigure(0, weight=0)
            self.config(height=2, relief='sunken', bd=1)
        else:
            self.columnconfigure(0, weight=0)
            self.rowconfigure(0, weight=1)
            self.config(width=2, relief='sunken', bd=1)





def create_unique_list (dataframe, column):
    """
    Extract sorted unique values from a dataframe column.
    NaN values are converted to 'Empty'.
    """

    try:
        itemsList = dataframe[column].unique().tolist()
    except:
        itemsList = []
    
    if(np.nan in itemsList):
        nan_index = itemsList.index(np.nan)
        itemsList[nan_index] = "Empty"
    
    itemsList.sort()

    if(np.nan in itemsList):
        itemsList.insert(0, itemsList.pop(itemsList.index("Empty")))

    return itemsList

