<span id="why-put-an-agent-in-the-application"></span>

# Why an embedded agent?

Today, many people use AI first when they need to get something done. They have
experienced how much faster it can be to compare options, understand something unfamiliar,
or work through an everyday task.

They bring those expectations to your application. If it leaves them searching through
menus, reading help pages and working out every step themselves, it can feel outdated—even
when its underlying capabilities are excellent.

<div class="story-image"><img src="../images/wagon.png" alt="A covered wagon labeled Your App Name Goes Here, suggesting an application that feels outdated."></div>

An embedded agent can help people use those capabilities.

The opportunity is especially clear for useful features people encounter infrequently,
workflows spanning several screens, and workplaces where new staff repeatedly have to learn
the same application. Start with a job where those difficulties cost your users time or money.

<span id="connect-that-expectation-to-your-application"></span>

## Connect user goals to application capabilities

Your application may already do what a person needs. The difficulty is often discovering
that capability, learning its controls, and working out the sequence that completes the job.
An embedded agent can help people make that connection.

On an ecommerce site, a person might want to find a product that fits their needs, check
whether other buyers recommend it, complete a purchase, resolve a problem, or return
something unsuitable.

In a photography application, they might want to improve a poorly lit photo, find pictures
from a particular trip, organize a growing collection, or share selected photos with friends.

Each of these jobs may require several application capabilities. The person knows what they
want to accomplish, but may not know which controls to use or in what order.

!!! consider "Consider — where could an agent help first?"
    If you had an agent in your application or website, where would it help your users first?
    What are they struggling to accomplish today?

    Write down one example and what tells you it matters: support calls, repeated questions,
    abandoned tasks, or watching someone use the application.

## Poor assistance can make the experience worse

<div class="story-image"><img src="../images/laptop-toss.png" alt="A frustrated person tossing a laptop."></div>

An agent that changes the wrong thing, invents an ability, or says it saved something when
it did not adds uncertainty to an already difficult task.

Getting an agent to help with a few requests can be relatively easy. Making it reliably
helpful across the range of situations and language your users bring can require extensive
work. People leave things unstated, use different terms, change their minds, and assume the
application understands their situation. Providing the capability is only part of the job;
the agent must also recognize when and how to use it—or when to ask a question.

That requires a deep understanding of your users, careful testing, and repeated improvement.
It also means learning from real use: with users' permission and appropriate privacy
protections, examine production interactions to see where people struggle, where the agent
misunderstands, and what needs to change. Plan how to capture and review those interactions
under your organization's policies, and use what you learn to guide ongoing improvements.

## From finding help to doing the job together

[![Six levels of assistance, with learning about the person and noticing outdated information supporting levels two through six.](../images/assistance-levels.svg)](../images/assistance-levels.svg)

*Help search and help search with AI find instructions. Tell me how, show me how, do it for me,
and do something new connect assistance to the working application. Learn about me supports
levels 2–6.*

Search is useful when it quickly gets people to the information they need. Basic keyword
search can return many irrelevant results, especially for common terms. AI-assisted search
can improve relevance, but the person still has to understand the information and apply it
in the application.

An embedded agent can connect that information to what the person is doing—explaining the
next step, pointing to the relevant control, or carrying out an authorized task. It can also
combine operations into a workflow nobody provided a dedicated button for.

Match the response to the request. "How do I?" calls for instruction, "Show me" for a
demonstration, and "Do it" for action. The person's request determines which kind of assistance
is appropriate.

One kind of support runs alongside levels 2–6. "Learn about me" builds the
application's understanding of the person's goals, preferences, and circumstances, and keeps
it up to date. This can improve assistance across those levels. The chapter
[Learn about me](onboarding.md) shows ways to provide it.

## Start with the job people want to accomplish

Start with what the person is trying to accomplish. Someone replacing a broken washing
machine wants one that fits their space and budget, will last, and can be delivered before
the laundry piles up. Search, filters and comparison controls help them make that choice.

Understanding that job helps you decide where an agent could help and which capabilities
it needs: checking dimensions, comparing products, reviewing information about reliability,
confirming availability and arranging delivery. The agent can help assess likely durability
using available evidence; it cannot promise how long the machine will last.

A job to be done is what someone is trying to accomplish in a particular situation.
It is a way to understand the need before choosing a feature or a solution. You can use
that distinction when reviewing everyday requests and support calls. Jim Kalbach's
[*The Jobs To Be Done Playbook*](https://rosenfeldmedia.com/books/jobs-to-be-done-book/)
is a practical introduction to understanding customer needs and desired outcomes.

If you already use user stories, use cases, or support-call reasons, start with those.
Identify the result the person needs, as well as the feature they request. "Add more product filters"
names a solution. "Find a replacement part that fits the equipment I own" describes a job.
People may know what is broken without knowing a model number, a part name, or how to
check compatibility.

Start with a recurring difficulty that matters to your users. For example, repeated support
calls and returns may show that people struggle to choose compatible replacement parts.
An agent could help identify their equipment and use the application's product data to
check which parts fit. Before building that assistance, decide how you will tell whether
it helps: can people find a suitable part with less effort, fewer incorrect purchases, and
fewer calls to support? Check that calls dropped because people got the help they needed,
while keeping human support easy to reach.

![A repeating improvement cycle: find a recurring difficulty, build useful assistance, check whether it helped, and choose the next priority.](../images/improvement-cycle-blue.svg)

*Check the result before deciding what to improve next.*

Watch people use the assistance and review what happened. If they still struggle, use what
you learn to improve it. If it works well enough, address the next priority while continuing
to monitor it. Judge the assistance by whether the person achieved the intended result,
using both the application's records and the person's experience.

!!! practice "Practice — describe one job"
    For the application you chose, write three sentences: the person's situation, what they
    want to accomplish, and how they would know it was done. Describe the outcome in the
    person's terms. Then note how they do it today. Keep this example for the next chapters.

<span id="users-use-two-languages"></span>

## Two ways people ask

<p class="section-subhead">The language of the application and the language of the job</p>

Applications teach us useful ways to think about our work. Someone who has never used a
paper spreadsheet can learn to organize information in rows, columns, and sheets through
Excel. Those concepts become part of how they think about their work.

![Familiar words learned from presentation software, spreadsheets, online stores, email, and music applications.](../images/apps-teach-language.svg)

*Familiar application vocabulary includes a deck, a cell, a pivot table, add to cart,
out of office, reply all, and a playlist.*

An agent should understand both languages. A person may describe an outcome—"show me sales
by region"—or ask directly for a pivot table. The agent should respond to the way the person
chooses to ask.

![Examples of requests expressed as desired outcomes and in the application's familiar language.](../images/two-languages.svg)

*Paired requests for finding a charger, viewing regional sales, and letting people know
about an absence.*

A person may ask for "something to stop this pipe leaking" or "a half-inch compression fitting."
A helpful hardware-store clerk understands both. Tool names and descriptions should similarly
connect what people want to accomplish with the familiar names of the application's controls
and operations. When someone names a specific operation, the agent should respect that choice;
when the request is unclear, it should ask for the information it needs.

!!! consider "Consider — what language do your users already use?"
    Which terms from your application have become part of how users describe their work?
    Listen for both the outcomes they want and the controls or operations they name.
    Write down examples of each and the capabilities they would use.

To put this assistance into practice, connect the agent to the application's capabilities.
Depending on the job, it may also need to see and control the UI. The next chapter,
[Shared capabilities and the registry](design.md), explains how to build that connection:
the person and the agent use shared application operations, while code enforces the
permissions and approval requirements appropriate to each.
