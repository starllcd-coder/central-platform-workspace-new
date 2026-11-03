"use client";

import * as React from "react";

export function useDisclosure(defaultOpen = false) {
  const [open, setOpen] = React.useState(defaultOpen);

  const onOpen = React.useCallback(() => setOpen(true), []);
  const onClose = React.useCallback(() => setOpen(false), []);
  const onToggle = React.useCallback(() => setOpen((value) => !value), []);

  return {
    open,
    setOpen,
    onOpen,
    onClose,
    onToggle
  };
}
