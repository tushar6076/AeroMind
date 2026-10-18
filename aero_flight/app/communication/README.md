# Communication boundary

Reserved for verified serial/protocol adapters and their transport contracts.
Candidate interfaces include CRSF receiver telemetry and Betaflight MSP, but
the exact UART, baud rate, serial-port function, and ownership are not yet
verified for the installed FC722 revision.

Do not duplicate Aero Cloud's existing CRSF service until an architecture
change explicitly assigns one owner for the physical link.
