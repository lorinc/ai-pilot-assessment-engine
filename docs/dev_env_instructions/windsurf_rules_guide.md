## Rule-writing best practices 
- Be specific and concise: Avoid generic rules like "write good code." Instead, specify exactly what is needed, such as "When creating React components, always use TypeScript interfaces for props".
- Use clear formatting: Use bullet points, numbered lists, and markdown to make rules easy for the AI to understand.
- Group similar rules: Use XML tags to group related rules, which can improve organization.
- Prioritize simplicity: Start with a small set of essential rules and avoid overwhelming the system with too many.
- Follow project conventions: Document rules that align with your team's specific development practices, such as preferred libraries or error handling methods.
- Use early returns: When possible, use early returns in your code for clarity.
- Document new functions: Always add documentation when creating new functions and classes. 
## Coding style best practices
- Keep components and files cohesive: Aim to keep files and modules focused, with a general target of under 250 lines.
- Break down complexity: Avoid overly long and complex functions. Instead, break them down into smaller, more focused, and functional components.
- Avoid mutations: Wherever possible, try to avoid mutating state and using global state.
- Use functional components: Write functional components with proper types for props.
- Implement TypeScript: Use TypeScript for type safety, especially for props in React components. 
## Implementation and refinement
- Start small: Begin with 5–10 essential rules before expanding.
- Test incrementally: Test rules in small features before applying them more broadly.
- Involve the team: Get team feedback to shape and refine the rules.
- Update regularly: Update the rules as your project evolves.
- Trust the code: When in doubt, trust what the running code actually does over documentation. 