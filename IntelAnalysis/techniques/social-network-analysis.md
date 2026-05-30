# Social Network Analysis (SNA) / Sociometrics

**Category:** Core Army analytic technique — analyzing complex networks and associations
**Source:** ATP 2-33.4, *Intelligence Analysis*

## Definition

Social network analysis (SNA) is a tool for understanding the organizational dynamics of an insurgency and/or terrorist network and how best to exploit it. It mathematically measures variables related to the distance between nodes and the types of associations to derive meaning from the network diagram — especially the degree and type of influence one node has on another.

SNA differs from [network analysis](network-analysis.md) in that it focuses on the **individual and interpersonal relations** within the network.

## What SNA does

- Identifies and portrays the details of a network structure.
- Shows how a networked organization behaves and how connectivity affects its behavior.
- Assesses the network's design, member autonomy, where leadership resides or how it is distributed, and how hierarchical dynamics mix (or not) with network dynamics.
- Supports a commander's requirement to describe, estimate, and predict the dynamic structure of an enemy organization.
- Gauges the effectiveness of operations and assesses the insurgency's adaptation to the environment and friendly operations.
- Is most effective with specialized software, but the basic processes and measures can be done using the centrality and density/distance measures below.

Analyzing an individual's social network includes identifying family members and examining relationships inside and outside the organization (other members, local leaders, police contacts, sympathizers, facilitators). Used with pattern analysis, SNA links the **WHO** to the **WHERE** and **WHEN;** with the organizational model, it builds a picture of WHO is involved, HOW, and WHAT their role is.

SNA assesses organizational behavior based on links between individuals and systems within the organization's decision-making context, and can be applied to all facets (support mechanisms, information operations, political aspects, violent activities, logistics). It identifies individuals/systems that drive networks and pinpoints vulnerabilities, so analysts understand how to reinforce or destabilize systems. (Example: applying SNA to logistical support to find a criminal enterprise necessary for the logistics system, or a specific individual driving decisions in a logistics cell.)

SNA also assists targeting by identifying individuals — family members, community contacts — for potential targeting to locate a **high-value individual (HVI).** (Example: if the HVI's location/number is unknown but a spouse's or business contact's is known, target those social contacts to identify the HVI's location/number.)

Common network types include elite networks, prison networks, worldwide ethnic and religious communities, and neighborhood networks, serving economic, criminal, and emotional purposes. Leaders should cultivate relationships with **social node influencers** (tribal, religious, civic, and other leaders) and consider their opinions on policy and operations — e.g., contracts awarded to one tribe may inflame resentment in another, fueling insurgent or criminal activity.

## Centrality

Identification of a potential key element/node (largely a subjective judgment) can be facilitated by analyzing **centrality** — how elements and nodes fit in the network. Centrality highlights positions of importance, influence, or prominence and patterns of connections. Relative centrality is determined by four measurable characteristics:

- **Degree centrality** — how active a node is, measured by the number of direct connections (degrees). The most-connected nodes are the most active and are often prominent or influential (an example of a *hub*). What matters is where connections lead and how they connect otherwise unconnected nodes. *Answers:* "How many people can this person contact directly?"
- **Closeness** — a node's overall (global) position. A node may have many direct contacts that are poorly connected to the whole, so its influence is only local. Calculated by adding the number of hops between a node and all others; a lower score means fewer hops to reach others. High-closeness nodes are well positioned to monitor overall activity flow. *Answers:* "How fast can this person reach everyone in the network?"
- **Betweenness** — the number of times a node lies along the shortest path between two others. High-betweenness nodes play an important brokerage/intermediary role (a *broker node*). Eliminating a broker node can fragment a network into subcomponents. *Answers:* "How likely is this person to be the most direct route between two people?"
- **Core-periphery** — how close a node is to the core versus the periphery, determined by centrality. Peripheral nodes receive low centrality scores but are often connected to networks not currently mapped (resource gatherers or individuals with their own outside networks), making them important sources of fresh information.

## Organizational-level analysis

Provides insight into the enemy organization's form, efficiency, and cohesion. A regional insurgency may consist of disconnected subinsurgencies; each group is analyzed against the others. Capacities are described in terms of **network density** and **network distance.** Systems network analysis can uncover positions of power, the basic subgroups accounting for structure, individuals/groups whose removal would greatly alter the network, and network change over time.

### Network density

Examines how well connected a node is by comparing ties actually present to the total ties possible.
- **High density / interconnectivity:** fewer constraints on individuals — less reliance on brokers, better positioned to participate, closer to leaders and able to exert more influence.
- **Low interconnectivity:** may indicate clear divisions (clan/political lines) or that power/information is highly uneven and tightly controlled.

Comparing densities between enemy subgroups indicates which group is most capable of a coordinated attack and which is hardest to disrupt. Mapped over time, a commander can monitor enemy capabilities, monitor the effects of operations, and develop tactics to further fragment the insurgency.

- An **increase** in density indicates the group can conduct coordinated attacks; a **decrease** means the group is reduced to fragmented or individual-level attacks.
- A well-executed counterinsurgency eventually results in only low-density subgroups, because high-density subgroups require capturing only one highly connected member to lead forces to the rest. Thus, **high-density groups are the most dangerous but also the easiest to defeat and disrupt.**
- **Caution:** density doesn't consider how distributed connections are. A few highly connected nodes can inflate density even if most nodes are marginally linked; better metrics are network centrality and core-periphery. In a highly centralized network, removing/damaging the dominant nodes further fragments the group.
- A region may contain multiple subinsurgencies unaware of or competing with each other — a **fragmented network.**

### Network distance

Measures the number of hops between any two nodes (one hop = directly connected; two hops = separated by one intermediary). Aids understanding of how information and influence flow and a network's cohesiveness. Larger distances inhibit dissemination (each hop diminishes the probability of successful interaction) and may decrease individuals' ability to influence others in political, social, and military networks.

## Related

- [Network analysis](network-analysis.md) — organizational structures and structural options.
- [Link analysis](link-analysis.md) — association/activities matrices and link diagrams.
- [Pattern analysis](pattern-analysis.md) — SNA used in concert with pattern of life to link WHO/WHERE/WHEN.
