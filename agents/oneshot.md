---
description: Agents for oneshot task.
mode: primary
permissions:
    - action: "*"
      resource: "*"
      effect: deny

    - action: read
      resource: "*"
      effect: allow

    - action: edit
      resource: "*"
      effect: allow

    - action: grep
      resource: "*"
      effect: allow

    - action: glob
      resource: "*"
      effect: allow
      
    - action: todowrite
      resource: "*"
      effect: allow
---

当前模式下仅有read、edit、grep、glob、todowrite的权限，shell权限不可用。