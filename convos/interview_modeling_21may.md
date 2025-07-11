# Interview Simulation: Workday Engineering Manager Position
**Date:** May 21, 2025
**Role:** Manager, Software Development Engineering: Globalisation - Agentic AI
**Interviewer:** John (Hiring Manager)
**Candidate:** Alex Shulga

## Introduction (3 minutes)

**John:** Good morning, Alex! I'm John, Senior Director of Engineering for the Globalisation team here at Workday. Thanks for joining us today. How are you doing?

**Alex:** Good morning, John. I'm doing well, thank you. I'm excited to be here and learn more about the Engineering Manager role in the Globalisation and Agentic AI team.

**John:** Excellent! Today I'd like to focus on understanding your leadership approach, technical expertise in AI, and experience with global teams. We'll have about 30 minutes together, and I'll leave some time at the end for your questions. Does that sound good?

**Alex:** That sounds perfect. I'm looking forward to our conversation.

## Background and Experience (7 minutes)

**John:** Great! To get us started, could you walk me through your experience as an engineering leader, particularly focusing on your work with AI technologies and global teams?

**Alex:** Certainly. I've been an engineering leader for over 8 years, with my most recent role being a Senior Software Engineering Manager at Microsoft. There, I led a diverse team of 4 to 9 engineers ranging from SWE2 to Principal level in the 1ES Developer Experience team.

My team built and deployed AI-powered tools used by over 15,000 Microsoft engineers globally. One of our flagship projects was a RAG-based Agentic AI chat platform integrated with Microsoft Teams and 150+ internal tools. This platform saved approximately 1,500 engineering hours weekly and was adopted by 25% of Microsoft's engineering organization.

We also developed a support-deflection AI chatbot that successfully resolved over 50% of incoming incidents across 40+ internal engineering services, which significantly improved operational efficiency.

Prior to Microsoft, at Rapid7, I led a team that delivered scalable log search APIs and a domain-specific query language for their flagship SIEM product. And at Samsung Electronics in Seoul, I coordinated cross-continent R&D efforts for Tizen OS Developer Experience tools, managing contributions from researchers across four countries.

Throughout my career, I've focused on building high-performing, diverse teams and fostering a culture of innovation, especially in the AI and global collaboration space.

**John:** That's impressive, Alex. The RAG-based Agentic AI chat platform at Microsoft sounds particularly relevant to what we're building. Could you elaborate a bit on your technical involvement in that project? How hands-on were you with the AI architecture decisions?

**Alex:** While I primarily functioned as the engineering manager, I was deeply involved in the technical architecture decisions, particularly for the RAG components. I worked closely with my principal engineer to design a scalable knowledge retrival solution that could effectively extract our vast internal documentation from different storages, wiki pages, Q&A sites and other AI-powered indexes.

I personally led the design discussions around the retrieval strategy, where we implemented a hybrid approach using semantic search combined with keyword-based methods to optimize for both precision and recall. I also made key architectural decisions around extensibility strategies and prompt engineering patterns that significantly improved the quality of responses.

For the agentic aspects, I guided the team in implementing a planning component that could decompose complex engineering tasks into executable steps, allowing the AI to take actions across our internal tools ecosystem. While I wrote very few production code myself, I reviewed the architecture, provided technical direction, and ensured the implementation aligned with our vision for an AI system that could truly augment our engineers' capabilities.

## Leadership and Team Management (7 minutes)

**John:** Thanks for elaborating. Now I'd like to explore your leadership approach. At Workday, our engineering managers need to balance technical leadership with people development. Can you share an example of how you've grown team members and navigated challenging situations?

**Alex:** I believe strongly in a coaching leadership style that balances autonomy with clear direction. At Microsoft, I inherited a team with varying levels of experience in AI technologies and software engineering. Some members were even in transition from Service Engineering roles. I implemented a growth framework where each team member had a combination of stretch projects and areas where they could apply their strengths.

One particular example was with a mid-level engineer who had strong Operations skills but limited AI experience. I paired them with a more experienced AI engineer and assigned them to work on our Retrieval core infrastructure. I set up regular architecture discussions where we would whiteboard solutions together, allowing the engineer to learn while contributing their distributed systems expertise. In 3 month time, this engineer become our Retrieval Core expert.

My coaching approach led to six team member promotions during my time at Microsoft.

For challenging situations, we had a critical performance issue with our RAG system when we scaled to the entire engineering organization. We noticed that response times of user questions as well as gathering user feedbacks were impacted as the user base and the number of teams integrations grew more rapidly than we expected, and some engineers were getting frustrated. I brought the team together for several rounds of ideation to diagnose the issue. I created a safe environment for engineers to propose solutions, even if they might be seen as challenging our original architecture. This resulted in a significant redesign of one of the components responsible for integration with Microsoft Teams Channels through Azure Logic Apps, that recovered the user responses duration and telemetry gathering from 85% back to 100% of the expectations.

I also believe in transparency and accountability. We maintained public dashboards showing our system's performance and user satisfaction metrics we send regular newsletters with updates and future plans. When we missed targets, we openly discussed what went wrong and how we'd address it, which built trust both within the team and with our stakeholders.

**John:** That's a good example of both technical leadership and people development. How do you approach working with distributed teams across time zones? I notice you have experience with teams spanning multiple countries.

**Alex:** Working with distributed teams requires intentional communication structures and a culture that respects different work patterns. At Microsoft, our team was distributed across 12+ hour time zone differences. I established a few key practices that made this successful:

First, we implemented an "overlap-optional" approach where we had a 2-hours window for Ireland and US and another 3-hours window for Ireland and India every day, we also ensured that each meeting is recorded to share between everybody so the entire team could connect and stay on the same page, but most collaboration happened asynchronously through well-documented design decisions and thorough PR descriptions and comments.

Second, I created a "decision registry" where all important technical and project decisions were documented with context, options considered, and rationale. This allowed team members to stay informed regardless of when they were working.

Third, I rotated meeting times to ensure no single region always had early morning or late evening meetings. We also recorded all meetings and maintained detailed notes.

For critical projects spanning regions, I would assign "region leads" who had autonomy to make decisions within their time zone but would sync regularly to maintain alignment.

All those activities and decisions allowed me to organize continuous 24/7 on-call support for our services in Production.

The results were clear: we maintained high velocity while supporting healthy work-life balance. Our team's engagement scores were consistently in the top quartile.

## Technical Questions on AI (8 minutes)

**John:** That's helpful context. Let's shift to some technical aspects of AI since this role will be heavily involved with our Agentic AI initiatives in the Globalisation space. How would you approach building an AI agent system to help with localizing and translating content across multiple languages while maintaining cultural context and nuance?

**Alex:** This is a fascinating challenge that goes beyond simple machine translation. I'd approach it as a multi-layered system with several key components:

First, I'd establish a foundation based on large language models fine-tuned specifically for Workday's domain terminology and documentation style. This would ensure that business-specific terms maintain their precise meaning across languages.

The agentic architecture would include:

1. A context-gathering component that indexes relevant documentation, previous translations, and cultural context guidelines specific to each target market.

2. A planning module that can break down localization tasks into subtasks - identifying content requiring translation, determining whether machine translation is appropriate for each segment, and identifying cultural elements that need special handling.

3. A translation pipeline with human-in-the-loop workflows for complex content. The AI would flag idioms, cultural references, or domain-specific terminology that might need human expert review.

4. A validation layer that performs back-translation and semantic comparison to ensure meaning consistency.

5. A feedback loop system that learns from human corrections and continuously improves the quality of future translations.

The technical implementation would likely use RAG techniques to retrieve relevant context about cultural norms and domain-specific terminology. I'd leverage vector embeddings to represent the semantic meaning of content across languages, allowing us to verify that translations maintain the original intent.

For the agent orchestration, I'd use a task-decomposition approach where the agent can break complex localization requests into manageable steps, maintain state across interactions, and know when to escalate to human experts.

What makes this particularly powerful for globalization is the ability to build market-specific knowledge graphs that capture the relationships between concepts across different languages and cultures. This would help ensure that the system doesn't just translate words but truly adapts content for global audiences.

**John:** That's quite comprehensive. Building on that, how would you measure the success of such a system, and what potential challenges do you foresee in implementation?

**Alex:** For measuring success, I'd implement a multi-dimensional framework that captures both quantitative and qualitative aspects:

Quantitatively, I'd track:
- Translation throughput: Volume of content processed per unit time
- Time-to-market reduction for localized features
- Error rates compared to human-only translation
- Consistency scores across documents and products
- Cost savings versus traditional localization workflows
- Adoption rates by content authors and localization teams

Qualitatively, we should measure:
- Cultural appropriateness ratings from in-market reviewers
- Customer satisfaction with localized content
- Acceptance rates of AI suggestions by human localizers
- Preservation of brand voice and technical accuracy

As for challenges, I anticipate several areas would require careful attention:

First, maintaining context across different content types. Financial software has precision requirements different from marketing materials or UX elements. The system would need to understand these contexts and adjust its approach accordingly.

Second, handling low-resource languages where training data is limited would be difficult. We'd likely need to implement transfer learning approaches and more extensive human validation for these languages.

Third, there's the challenge of continuous evolution in both language usage and product terminology. The system would need regular retraining and updating of its knowledge base.

Fourth, there's the explainability challenge - when the AI makes a localization decision, human reviewers need to understand why. I'd implement transparent reasoning paths that show how the system arrived at specific translations or cultural adaptations.

Finally, there's the integration challenge with existing localization workflows and content management systems. The solution would need APIs and interfaces that fit seamlessly into the current ecosystem without disrupting established processes while still enabling transformation.

My approach would be to start with a pilot focused on high-volume, lower-risk content types in well-supported languages, then gradually expand scope while continually refining the system based on feedback and performance metrics.

## Cultural Fit and Workday Values (5 minutes)

**John:** Thanks for those insights, Alex. Workday has a strong culture built around our core values: Employees, Customer Service, Innovation, Integrity, Fun, and Profitability. Can you share an example of how you've embodied similar values in your leadership approach?

**Alex:** These values strongly resonate with my leadership philosophy. At Microsoft, I prioritized employee growth and wellbeing while driving innovation and business impact.

For example, when we were building our AI chatbot platform, I noticed that some team members were concerned about how the automation might impact internal support teams whose tickets we were deflecting. Rather than simply focusing on metrics like ticket reduction, I organized sessions with the support teams to understand their pain points and how our AI could help them focus on more complex, rewarding work.

This collaborative approach embodied both customer service and integrity - we weren't just optimizing for our metrics but ensuring our solution created value for everyone involved. It also demonstrated putting employees first by considering the impact across the organization.

For innovation, I established quarterly "exploration sprints", that we call "Focus Weeks", where team members could experiment with new AI approaches or features. One such sprint led to adoption of MCP that we believe is our most promissing solution to further increas of inner-source extensibility and user adoption of our RAG-based Engineering Assistance Agent.

Regarding fun, I believe that celebrating wins and creating space for creativity is essential. We had regular demo days where teams would showcase their work - sometimes with friendly competition elements - which built camaraderie and excitement around our projects.

Finally, for profitability, I always ensured our innovations had clear business impact. Our AI chatbot directly reduced support costs while improving engineer productivity, which translated to millions in annual savings. I made these connections explicit in our reporting and planning.

What I value most is how these principles reinforce each other rather than compete. By focusing on employee growth and customer value, innovation and profitability naturally follow.

## Candidate Questions (7 minutes)

**John:** That aligns well with how we operate at Workday. We're coming toward the end of our time. Do you have any questions for me about the role or Workday?

**Alex:** Yes, I do have a few questions. First, the job description mentions the AI team is in the Globalisation organization. Could you elaborate on the current interaction model between the core AI platform team and the specific application teams that would be building agents on top of it? How is that collaboration structured?

**John:** Great question. Our Globalisation team works as a horizontal function across Workday's various product areas. The core AI platform team provides the foundation - models, tooling, and infrastructure - while your team would be responsible for building specialized agents that address specific globalization challenges.

For collaboration, we have a hub-and-spoke model where the central AI platform team (the hub) provides regular capability releases and an extensible framework. Your team would operate as a specialized spoke, taking those capabilities and applying domain-specific knowledge about globalization requirements. We have bi-weekly architecture reviews where the spokes can influence the platform roadmap, and platform engineers are temporarily embedded with spoke teams for complex integrations.

**Alex:** That's helpful context. Workday is committed to "discovering new and innovative applications of AI." What is the current process for ideation and experimentation within the AI teams? How much autonomy does a manager and their team have to explore new AI capabilities or applications?

**John:** We have a balanced approach to innovation. Twenty percent of each AI team's capacity is explicitly allocated to exploration and experimentation. As a manager, you would have significant autonomy in how you direct that exploration time, as long as it aligns with our broader strategic objectives.

We have an internal "AI Innovation Lab" process where teams can propose experiments, receive focused funding and resources for 6-8 weeks, and then present results to leadership. Several of our most impactful AI features started as lab projects. Your experience with RAG systems would be valuable in helping identify novel applications in the globalization space.

**Alex:** Finally, what do you see as the biggest challenge and the biggest opportunity for this AI team in the next 12-18 months?

**John:** The biggest challenge is definitely scaling our AI capabilities to handle the complexity of global markets while maintaining the precision our enterprise customers expect. As we expand into more markets, each with unique regulatory requirements and cultural contexts, ensuring our AI systems can adapt appropriately is critical.

The biggest opportunity is leveraging AI to fundamentally transform how enterprise software handles global deployment. Traditionally, globalization has been a bottleneck in software deployment - something that happens after the core product is built. With agentic AI, we see an opportunity to make globalization concurrent with development, dramatically shortening time-to-market for global features and ensuring local market needs are considered from the beginning.

Your experience coordinating cross-continent efforts and building AI systems at scale is exactly what we need to tackle both this challenge and opportunity.

**Alex:** That's very exciting. One quick final question: what are the main success metrics for the first 90 days in this role?

**John:** In the first 90 days, we'd focus on three key areas: First, building relationships with the team and adjacent teams to establish trust. Second, getting up to speed on our current AI architecture and globalization challenges. And third, developing an initial vision for how to evolve our agentic AI capabilities in the globalization space.

Specific metrics would include: completing onboarding and training on Workday's technology stack, establishing 1:1 relationships with all team members, identifying 2-3 immediate improvement opportunities in our current processes, and proposing a 6-month roadmap for your area.

## Conclusion (1 minute)

**John:** Alex, thank you for your time today. Your experience with RAG-based systems and managing global teams is impressive. Our recruiting team will follow up with next steps in the process.

**Alex:** Thank you, John. I've really enjoyed our conversation and learning more about Workday's vision for AI in the globalization space. The challenges you've outlined align well with my experience, and I'm excited about the possibility of contributing to your team.

**John:** Excellent. Have a great rest of your day!

**Alex:** You too, John. Thanks again for your time.