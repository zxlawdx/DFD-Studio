# ADR 0001: reduced Vela layering for DFD Studio

## Status
Accepted.

## Decision
Use four recognizable responsibilities—presentation, application, domain and infrastructure—but keep each as small as the project requires. Existing import paths stay as compatibility shims during migration.

## Why
DFD Studio benefits from the same mental model as larger Vela apps, but creating dozens of empty directories would add ceremony without reducing coupling.
