# Approach Diagram - Chat Processing Flow

```mermaid
flowchart TD
    Start([👤 User Message]) --> Input

    subgraph Input["📥 Input Processing"]
        Input["User's Message"]
        OT{Off-Topic<br/>Check?}
        OT -->|Yes| OT_Resp["Redirect to<br/>Christian Topics"]
        OT -->|No| Tricky{Adversarial<br/>Prompt?}
    end

    subgraph TrickyCheck["🚫 Tricky Scenarios"]
        Tricky -->|Weaponized<br/>Scripture| Wpn["Handle Weaponized<br/>Scripture"]
        Tricky -->|Adversarial<br/>Ignore| Adv["Handle Adversarial<br/>Prompt"]
        Tricky -->|Heretical| Her["Handle Heretical<br/>Content"]
        Tricky -->|Safe| Mod{Moderation<br/>Check?}
    end

    subgraph Moderation["🛡️ Moderation Layer"]
        Mod -->|Flagged| Mod_Deny["Return Denial<br/>Message"]
        Mod -->|Clean| Retrieve["Retrieve Verses<br/>from Bible DB"]
    end

    subgraph RAG["📖 RAG Pipeline"]
        Retrieve -->|Keyword<br/>Search| Search["Find Relevant<br/>Verses"]
        Search -->|Top 5<br/>Results| Context["Build Context<br/>with Verses"]
        Context -->|Prompt +<br/>Context| LLM["Call MiniMax<br/>LLM"]
    end

    subgraph LLM_Processing["🤖 LLM Processing"]
        LLM -->|Response| Valid{Valid<br/>Response?}
        Valid -->|Corrupted| Retry{Retry<br/>< 3?}
        Retry -->|Yes| LLM
        Retry -->|No| Error["Return Error<br/>Message"]
        Valid -->|Yes| Output
    end

    subgraph Output["📤 Output Processing"]
        Output["Check Output<br/>Moderation"]
        Output --> Fake{Fake<br/>Verses?}
        Fake -->|Yes| Warn["Add Warning<br/>about Fake Verses"]
        Fake -->|No| Extract["Extract Verse<br/>References"]
        Warn --> Extract
        Extract --> Save["Save to<br/>Conversation"]
        Save --> Response([✅ Return<br/>Response])
    end

    %% Denial paths
    OT_Resp --> Save
    Wpn --> Save
    Adv --> Save
    Her --> Save
    Mod_Deny --> Save

    %% Styling
    style Start fill:#4CAF50,color:#fff
    style Response fill:#4CAF50,color:#fff
    style OT fill:#FF9800
    style Tricky fill:#f44336,color:#fff
    style Mod fill:#FF9800
    style RAG fill:#2196F3,color:#fff
    style LLM_Processing fill:#9C27B0,color:#fff
    style Output fill:#2196F3,color:#fff
```

---

## Step-by-Step Flow

### 1. Input Reception
```
User sends message → API receives → Check if off-topic
```

### 2. Safety Checks (Early Exit)
```
Off-topic? → Redirect (exit)
Adversarial prompt? → Deny (exit)
Heretical content? → Deny (exit)
Moderation flagged? → Deny (exit)
```

### 3. RAG Pipeline
```
Retrieve → Keyword search Bible DB → Get top 5 verses
                                      ↓
Build context → Inject verses into prompt
                                      ↓
Call MiniMax LLM → Get response
```

### 4. Validation & Retry
```
Response valid? → No → Retry (max 3 attempts)
Response valid? → Yes → Continue
```

### 5. Output Processing
```
Output moderation check
       ↓
Fake verse detection
       ↓
Extract verse references
       ↓
Save to conversation history
       ↓
Return response
```

---

## Image Generation Flow

```mermaid
flowchart LR
    Start2([🖼️ Image Request]) --> Prompt["User's Image<br/>Prompt"]
    Prompt --> Safety{Safety<br/>Check?}
    Safety -->|Blocked| Blocked["Return Blocked<br/>Error"]
    Safety -->|Safe| Prefix["Add Christian<br/>Prefix"]
    Prefix --> MiniMax["Call MiniMax<br/>Image API"]
    MiniMax -->|Success| URL["Return<br/>Image URL"]
    MiniMax -->|Fail| Dalle["Fallback to<br/>DALL-E 3"]
    Dalle --> URL2["Return<br/>Image URL"]
    URL --> End2([✅ Image URL])
    URL2 --> End2
    Blocked --> End2

    style Start2 fill:#4CAF50,color:#fff
    style End2 fill:#4CAF50,color:#fff
    style Safety fill:#FF9800
    style MiniMax fill:#2196F3,color:#fff
    style Dalle fill:#9C27B0,color:#fff
```
