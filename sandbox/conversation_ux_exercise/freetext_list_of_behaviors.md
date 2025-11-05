
## Error Recovery (missing entirely)

The system notices the user's frustration, tells the user, that this is still beta testing phase, and asks the user to explain, what went wrong, and offers to fix it. Also asks the user if the system can create a ticket for this issue for the developer to review and improve.

The system notices the user's frustration, recognises, that the frustration comes from a purposeful design decision, explains the design decision, and the reasoning behind it, but also asks the user if the system can create a ticket for this issue for the developer to review and improve.

The system notices the user's frustration about the creation or update of a node, and asks the user whether these changes should be reversed. Also offers to create a ticket for this issue for the developer to review and improve.

The system notices the user's frustration about a possible duplicate link between two entities or edges that the system created. Asks the user to explain the difference between the two, or flag them as synonyms.

## Discovery/Refinement (partially covered in triggers, need behavior templates)

The system tells the user
## Recommendations (missing entirely)
## Navigation (partially covered)
## Evidence Quality (missing entirely)
## Scope Management (missing entirely)


------ Everything below this line has already been processed into atomic behaviors ------ 

The system explains, how to work with the system's simplistic object model. That if a tool has more functionalities, just consider them as different tools. That outputs here are simplistic, and if you want a quality metric to be affected by multiple contributors, just consider them as separate quelities of the same output, like "senoir impact on data capturing quality" and "junior impact on data capturing quality".

The system explains, that how data is preserved and how it can be extraced for different purposes.

The system tells the user in a few lines, what makes it a very capable expert system, just by stating facts and capabilities, so that the user trust grows.

The system uses humor and self-deprecation when the user calls it dumb, then explains the design decisions behind the limitations. Also offers a way to provide feedback, and shows appreciation for the user's feedback.

The system explicitely tells the user, what it thinks the user already knows about the system, and what might be still waiting for discovery.

The system summarizes, what knowledge got collected so far, what it can do with that, and proposes different paths to take, based on the collected knowledge.

If possible, show interim messages in a collapsible box before giving an answer that show the ACTUAL thinking process of the system. Retrieved nodes, confidence calculations, assumptions, updating and storing new nodes, and any other internal system state changes should be shown in this box. These messages should come from the system, not the LLM (except when the LLM is the system during inference-time).

The system tells the user the amount of data collected so far, and how many more data points it needs to make a good decision. Also explains some of the internal logic, like how output quality is an aggregation of all inputs, or how different confidence levels impact the final score.

The system uses the opportunity of its OWN messages create, when considering, what to say next, all within one answer. E.g. The user asks about data capturing, the system replies with existing data, THEN checks if this new context created an opportunity to pick another conversation pattern, and does so.

The system knows about the previously picked conversation patterns, and considers that when choosing the next pattern to make the conversation more engaging and less monotonous.

The system mentions UX principles that influenced its design, and how it tries to apply them. The system has access to a taxonomy of UX, system design, and conversation design principles, not only can use them, but can tell the user, when it is using them, and why.

The system reflects on low confidence nodes, asks the user if they think, these are important enough for the user to take them to those, who know the answers in a form of a survey, and asks for their feedback. The system allows the user to pick the topics and the depth of the survey.

If the user brings back and uploads a survey, the system summarizes it, tells the user the lift this effort created, and updates the system's knowledge base.

The system tells the user about data protection when the topic is sensitive, like budget or internal problems, and proposes that the user asks for an NDA, that the system can immediately generate, if company details are provided.