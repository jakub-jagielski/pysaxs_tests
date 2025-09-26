# PRINCIPIA - Comprehensive Testing Guide

## Overview
This document provides comprehensive testing scenarios for the Principia board game implementation. It covers all game mechanics, UI interactions, edge cases, and identifies discrepancies between the software implementation and the written instructions.

## Dependencies & Setup Testing

### 1. Initial Setup Tests
- [ ] **Python Environment**: Verify Python 3.7+ is installed
- [ ] **Module Dependencies**: Test import of all required modules:
  - `tkinter` and `ttk` (GUI framework)
  - `csv` (data loading)
  - `random` (game mechanics)
  - `math` (calculations)
  - `dataclasses` and `typing` (data structures)
  - `hex_research_system.py` (custom hexagonal map system)
- [ ] **File Dependencies**: Verify existence of CSV data files:
  - `karty_badan.csv` (Research cards)
  - `karty_naukowcy.csv` (Scientists)
  - `karty_czasopisma.csv` (Journals)
  - `karty_granty.csv` (Grants)
  - `karty_instytuty.csv` (Institutes)
  - `karty_konsorcja.csv` (Consortium cards)
  - `karty_intrygi.csv` (Intrigue cards)
  - `karty_okazje.csv` (Opportunity cards)
  - `karty_wielkie_projekty.csv` (Large projects)
  - `karty_kryzysy.csv` (Crisis cards)
  - `karty_scenariusze.csv` (Scenarios)
- [ ] **Fallback Data**: Test game startup when CSV files are missing or corrupted

## Game Launch & Initial UI Testing

### 2. Application Launch
- [ ] **Start Application**: Run `python principia_card_ui.py`
- [ ] **Window Creation**: Verify main window opens with correct title "Principia - Strategic Science Game"
- [ ] **UI Layout**: Check initial UI contains:
  - Left panel for player information
  - Center tabbed area (Game, Markets, Large Projects)
  - Right panel for research area
  - Bottom log area
- [ ] **Menu/Button Availability**: Verify "Nowa Gra" (New Game) button is present and clickable

### 3. Game Setup Testing
- [ ] **New Game Flow**: Click "Nowa Gra" and verify:
  - Scenario selection dialog appears
  - All 4 scenarios are present (Mars Race, Pandemic, Climate Crisis, AI Revolution)
  - Each scenario shows story, modifiers, max rounds, victory conditions
  - Scenario selection can be confirmed or cancelled
- [ ] **Player Initialization**: After scenario selection verify:
  - 3 players are created with different colors (Red, Blue, Green)
  - Each player has an institute assigned (MIT, CERN, Harvard, Cambridge, Stanford, Max Planck)
  - Starting resources match institute specifications
  - All players start with 3 reputation
- [ ] **Data Loading**: Verify successful loading of:
  - Research cards from CSV
  - Scientists from CSV
  - Journals from CSV
  - Grants from CSV
  - Large projects from CSV
  - Scenario and crisis data

## Core Game Mechanics Testing

### 4. Round Structure Testing
- [ ] **Round Progression**: Test complete round cycle:
  - Round 1 starts in Grant Phase
  - Players can select grants or receive government subsidy
  - Action Phase begins after all players select grants
  - Cleanup Phase processes salaries, grant completion, market refresh
  - Round 2 begins automatically
- [ ] **Phase Transitions**: Verify proper transitions between:
  - Grant Phase → Action Phase
  - Action Phase → Cleanup Phase
  - Cleanup Phase → Next Round Grant Phase
- [ ] **Turn Order**: Verify turn order rotates correctly each round

### 5. Grant Phase Testing
- [ ] **Grant Selection**: Test grant selection mechanics:
  - 6 grants are available each round
  - Each player can select maximum 1 grant per round
  - Grant values increase by 2K per round
  - Players who cannot/don't select grants get government subsidy
- [ ] **Grant Requirements**: Test requirement validation:
  - Grants with scientist type requirements
  - Grants with reputation requirements
  - Grants with publication requirements
  - Grants with research completion requirements
- [ ] **Government Subsidy**: Test fallback mechanism:
  - Automatically assigned when no valid grants available
  - Goal: 6 activity points in the round
  - Reward: 10K at round end
  - Activity point calculation: hire(2p), publish(3p), complete research(4p), consortium(5p)

### 6. Action Phase Testing
- [ ] **Action Card System**: Test all 5 action card types:

#### RESEARCH Action Card (3 Action Points)
- [ ] **Basic Action**: Activate 1 PhD student → +1 hex (free)
- [ ] **Additional Actions**:
  - Activate doctor → +2 hexes (2 points)
  - Activate professor → +3 hexes (2 points)
  - Start new research → play card from hand (1 point)
- [ ] **MIT Bonus**: Professors give +1 extra hex for physics research

#### HIRE Action Card (3 Action Points)
- [ ] **Basic Action**: Take 1K from bank (free)
- [ ] **Additional Actions**:
  - Hire doctor from market → 2K salary/round (2 points)
  - Hire professor from market → 3K salary/round (3 points)
  - Hire PhD student → no salary (1 point)
  - Buy "Research Projects" card → 2 Research Points (1 point)
  - Buy "Opportunities" card → 1 Research Point (1 point)

#### PUBLISH Action Card (2 Action Points)
- [ ] **Basic Action**: Publish 1 article (free)
- [ ] **Additional Actions**:
  - Take 3K from bank (1 point)
  - Buy "Opportunities" card → 1 RP (1 point)
  - Commercial consulting → activate professor for 4K (1 point)

#### FINANCE Action Card (3 Action Points)
- [ ] **Basic Action**: Take 2K from bank (free)
- [ ] **Additional Actions**:
  - Contribute to consortium → 1 RP or 3K to chosen project (1 point per resource)
  - Found consortium → play consortium card from hand (1 point)
  - Emergency credit → +5K but -1 Reputation (2 points)

#### MANAGE Action Card (2 Action Points)
- [ ] **Basic Action**: Take 2K from bank (free)
- [ ] **Additional Actions**:
  - Refresh market → journals or research (2 points)
  - PR campaign → spend 4K for +1 Reputation (1 point)
  - Image improvement → spend 2 RP for +1 Reputation (1 point)

### 7. Hexagonal Research System Testing
- [ ] **Research Start**: Test starting new research:
  - Player selects research card from hand
  - Hex map displays correctly
  - Start hex is marked and accessible
  - End hex and bonus hexes are visible
- [ ] **Hex Placement**: Test hex placement rules:
  - First hex must be placed on START position
  - Subsequent hexes must be adjacent (no gaps)
  - Continuous path requirement to END position
  - Bonus hexes trigger immediate rewards
- [ ] **Research Completion**: Test research completion:
  - Reaching END hex triggers completion
  - Basic and bonus rewards are granted
  - All player hexes are returned for reuse
  - Research card moves to completed portfolio
- [ ] **Hex Resource Management**: Test 20-hex limit per player:
  - Players start with 20 hexes
  - Hexes are consumed during research
  - Hexes are returned when research completes
  - Warning when running low on hexes

### 8. Scientist Management Testing
- [ ] **Scientist Types**: Test all scientist types:
  - PhD Student: 1 hex, no salary
  - Doctor: 2 hexes, 2K salary
  - Professor: 3 hexes, 3K salary
- [ ] **Salary System**: Test salary mechanics:
  - Salaries paid during cleanup phase
  - First unpaid salary → -1 reputation
  - Subsequent unpaid salaries → no additional reputation loss
  - Unpaid scientists become inactive
- [ ] **Staff Overload**: Test overload penalty:
  - More than 3 scientists → +1K salary penalty for each
  - Penalty applies to all scientists, not just excess
  - Harvard exception: can have 3 professors at standard rate

### 9. Publication System Testing
- [ ] **Journal Selection**: Test publication mechanics:
  - Available journals in market
  - Cost in Research Points (RP)
  - Reward in Prestige Points (PZ)
  - Impact Factor correlation with rewards
- [ ] **Publication Requirements**: Test publication validation:
  - Player has sufficient Research Points
  - Reputation requirements for high-impact journals
  - Journal availability in market
- [ ] **Reputation Effects**: Test reputation-based restrictions:
  - Reputation 2: Cannot publish in 6+ PZ journals
  - Reputation 1: Cannot publish in 4+ PZ journals
  - Reputation 0: Additional consortium penalties

### 10. Consortium & Large Projects Testing
- [ ] **Consortium Creation**: Test consortium founding:
  - Player must have consortium card in hand
  - Select target Large Project
  - Become consortium leader
  - Other players can join freely (leader can reject for 1 PZ)
- [ ] **Resource Contribution**: Test project funding:
  - Players contribute RP and credits as specified
  - Progress tracking toward project requirements
  - Leader decides when to complete project
- [ ] **Project Completion**: Test completion rewards:
  - Leader gets enhanced rewards
  - Members get standard rewards
  - Project removed from available list
- [ ] **Large Project Types**: Test all 5 projects:
  - Fusion Reactor (22 RP + 20K + 2 physics research)
  - Superconductor (18 RP + 25K + 2 physics research)
  - Gene Therapy (15 RP + 30K + 1 professor + 1 biology research)
  - Mars Exploration (20 RP + 35K + 3 any research)
  - Nanomaterials (16 RP + 15K + 2 chemistry + 1 physics research)

### 11. Intrigue & Opportunity Cards Testing
- [ ] **Intrigue Card Usage**: Test negative effect cards:
  - Select intrigue card from hand
  - Choose target opponent (if required)
  - Confirm usage
  - Effect applied automatically
  - Card removed from hand
- [ ] **Opportunity Card Usage**: Test positive effect cards:
  - Select opportunity card from hand
  - Check condition requirements
  - Confirm usage
  - Effect applied to self
  - Card removed from hand
- [ ] **Card Conditions**: Test requirement validation:
  - "Min. 1 publication" → player.publications >= 1
  - "Active research" → player.active_research length > 0
  - "Reputation 3+" → player.reputation >= 3
  - "Completed research" → player.completed_research length > 0
  - "Min. 1 professor" → has professor in team
  - "Chemistry or physics research" → appropriate field research

### 12. Crisis & Scenario System Testing
- [ ] **Crisis Timing**: Test crisis activation:
  - Crises appear according to scenario schedule
  - Crisis cards revealed at specified rounds
  - Global effects applied to all players
  - Crisis cards remain visible after activation
- [ ] **Scenario Effects**: Test scenario-specific modifiers:
  - Mars Race: Physics research +1 hex, consortiums -1K cost
  - Pandemic: Biology research +2 hexes, medical publications +1 PZ
  - Climate Crisis: Chemistry research +1 hex, green tech +2K completion
  - AI Revolution: AI research benefits, tech sector bonuses
- [ ] **Victory Conditions**: Test scenario-specific end game:
  - Different PZ thresholds per scenario
  - Alternative victory conditions (research count, projects)
  - Game end triggers properly

## User Interface Testing

### 13. Main UI Components
- [ ] **Player Panel (Left)**: Test player information display:
  - Current player highlighted
  - Resource counts (Credits, RP, PZ, Reputation)
  - Scientist list with types and status
  - Active and completed research
  - Current grant and progress
- [ ] **Game Tab (Center)**: Test main game interface:
  - Current phase indicator
  - Available actions based on phase
  - Turn order display
  - Round counter
- [ ] **Markets Tab (Center)**: Test market interface:
  - Available scientists for hire
  - Available journals for publication
  - Market refresh mechanics
  - Purchase buttons and interactions
- [ ] **Large Projects Tab (Center)**: Test projects display:
  - All 5 large projects visible
  - Project requirements and rewards
  - Progress indicators for active consortiums
- [ ] **Research Area (Right)**: Test research interface:
  - Hand cards display
  - Research selection mode
  - Active research hex maps
  - Card preview functions

### 14. Interactive Elements Testing
- [ ] **Button States**: Test button enable/disable:
  - Actions only available during appropriate phases
  - Buttons disable when requirements not met
  - Visual feedback for available/unavailable actions
- [ ] **Card Interactions**: Test card-based interactions:
  - Hand card preview popups
  - Research card selection
  - Intrigue/Opportunity card usage buttons
  - Card text and requirement display
- [ ] **Dialog Boxes**: Test all popup dialogs:
  - Scenario selection at game start
  - Action confirmations
  - Target selection for intrigue cards
  - Research selection for starting
  - Error messages and warnings
- [ ] **Text Display**: Test information presentation:
  - Game log messages
  - Current phase and turn indicators
  - Resource and progress counters
  - Help text and tooltips

### 15. Input Validation Testing
- [ ] **Resource Constraints**: Test resource limit validation:
  - Cannot spend more credits/RP than available
  - Cannot hire without meeting salary requirements
  - Cannot publish without sufficient RP
  - Cannot perform actions without required scientists
- [ ] **Card Hand Limits**: Test hand size restrictions:
  - Standard hand limit: 5 cards
  - Max Planck exception: 7 cards
  - Hand overflow handling
  - Card drawing restrictions
- [ ] **Turn Order Validation**: Test turn sequence:
  - Only current player can take actions
  - Pass functionality works correctly
  - Turn advances to next player
  - Round progression triggers appropriately

## Edge Cases & Error Testing

### 16. Resource Exhaustion Scenarios
- [ ] **Zero Credits**: Test when player has no money:
  - Cannot hire paid scientists
  - Cannot pay salaries (reputation penalty)
  - Government subsidy as backup
  - Emergency credit action available
- [ ] **Zero Research Points**: Test when player has no RP:
  - Cannot publish articles
  - Cannot contribute RP to consortiums
  - Need to complete research to gain RP
- [ ] **Zero Hand Cards**: Test empty hand scenarios:
  - Cannot start new research
  - Pass bonus increases with fewer cards
  - Card purchase actions available
- [ ] **Hex Exhaustion**: Test when player has no hexes:
  - Cannot progress research
  - Need to complete research to recover hexes
  - Multiple simultaneous research limitations

### 17. Boundary Conditions
- [ ] **Maximum Values**: Test upper limits:
  - Reputation cap at 5
  - Large resource accumulations
  - Maximum scientists and overload penalties
  - Hand size limits and drawing restrictions
- [ ] **Minimum Values**: Test lower limits:
  - Reputation minimum at 0
  - Resource minimums at 0 (cannot go negative)
  - Minimum turn requirements
  - Required actions vs optional actions

### 18. Data Corruption & Recovery
- [ ] **Missing CSV Data**: Test when data files are missing:
  - Fallback data generation
  - Error message handling
  - Graceful degradation
- [ ] **Invalid CSV Data**: Test malformed data handling:
  - Parse error recovery
  - Default value substitution
  - User notification of issues
- [ ] **Game State Corruption**: Test inconsistent game states:
  - Invalid player states
  - Resource count mismatches
  - Turn order corruption

## Performance & Usability Testing

### 19. Performance Testing
- [ ] **Game Start Time**: Measure application startup duration
- [ ] **UI Responsiveness**: Test interface response times:
  - Button clicks
  - Dialog opening
  - Card preview generation
  - Market refresh operations
- [ ] **Memory Usage**: Monitor memory consumption during:
  - Extended gameplay sessions
  - Multiple game restarts
  - Complex game states with many cards/scientists

### 20. Usability Testing
- [ ] **Learning Curve**: Test new user experience:
  - Clarity of initial interface
  - Availability of help/instructions
  - Error message helpfulness
  - Recovery from mistakes
- [ ] **Workflow Efficiency**: Test common operations:
  - Time to complete typical actions
  - Number of clicks for common tasks
  - Keyboard shortcuts availability
  - Undo/redo functionality

## Software vs Instructions Discrepancies

### 21. Identified Discrepancies

#### Missing Features in Software:
- [ ] **Institute Specializations**: Instructions describe 6 institutes with unique abilities:
  - Harvard: 3 professors max, +1 hex for professors, +1K salary penalty
  - State University: Unlimited doctors, 0.5K doctor salary, 1 professor max
  - Bell Labs: +3K income/round, immunity to reputation penalties, no government grants
  - Max Planck: 7 card hand limit, RP storage between rounds, +1K salary penalty
  - MIT: Physics specialization (implemented)
  - CERN: Physics specialization, consortium bonuses (partially implemented)
- [ ] **Detailed Grant System**: Instructions show complex grant requirements not fully implemented
- [ ] **Publication Restrictions**: Reputation-based journal access limitations
- [ ] **Equipment Cards**: Instructions mention equipment cards (marked as removed)
- [ ] **Pass Bonuses**: Different credit bonuses based on hand size when passing

#### Implementation Differs from Instructions:
- [ ] **Action Point System**: Instructions show variable action points per card, software uses fixed
- [ ] **Salary Rates**: Instructions show different salary progression than implemented
- [ ] **Grant Scaling**: Instructions mention +2K per round for grants
- [ ] **Crisis Integration**: Crisis cards exist but integration may differ from instructions
- [ ] **Research Maps**: Hex map complexity may differ from instruction examples

#### Instructions Need Updates:
- [ ] **Software-Specific Features**: Instructions should document:
  - Actual UI layout and navigation
  - Software-specific shortcuts and features
  - Save/load functionality (if implemented)
  - Multiplayer vs single-player modes
- [ ] **Updated Game Balance**: Instructions reflect January 2025 balance changes:
  - Salary adjustments (Doctor 1K→2K, Professor 2K→3K)
  - Subsidy increase (6K→10K)
  - Staff overload penalties
  - Grant scaling mechanics

### 22. Instruction Completeness Assessment

#### Well-Documented Areas:
- [ ] Game overview and objectives
- [ ] Basic round structure
- [ ] Core mechanics (research, publication, grants)
- [ ] Example gameplay walkthrough
- [ ] Balance analysis and rationale

#### Areas Needing Documentation:
- [ ] **Software Installation**: Step-by-step setup instructions
- [ ] **UI Guide**: Screenshot-based interface tutorial
- [ ] **Troubleshooting**: Common issues and solutions
- [ ] **Advanced Strategies**: Tips for effective gameplay
- [ ] **Multiplayer Setup**: If supported by software
- [ ] **Customization**: How to modify cards/scenarios

#### Suggested Instruction Improvements:
- [ ] **Visual Aids**: Add screenshots of key game states
- [ ] **Quick Reference**: Summary cards for action types and costs
- [ ] **FAQ Section**: Common questions and answers
- [ ] **Version History**: Track changes between instruction versions
- [ ] **Software Mapping**: Direct correlation between rules and UI elements

## Final Recommendations

### 23. Testing Priority Matrix

#### Critical Tests (Must Pass):
- [ ] Game launches successfully
- [ ] Basic round progression works
- [ ] Core action cards function correctly
- [ ] Resource management enforced
- [ ] Victory conditions trigger properly

#### Important Tests (Should Pass):
- [ ] All card types work as intended
- [ ] UI provides clear feedback
- [ ] Error handling prevents crashes
- [ ] Data loading robust against missing files

#### Nice-to-Have Tests (Good to Pass):
- [ ] Performance under stress
- [ ] Advanced strategy validation
- [ ] Complete feature parity with instructions
- [ ] Professional UI polish

### 24. Test Execution Strategy

#### Phase 1: Smoke Testing
1. Basic application launch and game setup
2. One complete round with minimal actions
3. Basic win condition verification

#### Phase 2: Feature Testing
1. Systematic testing of each action card type
2. All game mechanics validation
3. UI component verification

#### Phase 3: Integration Testing
1. Complete multi-round games
2. Complex scenario testing
3. Edge case validation

#### Phase 4: Polish Testing
1. Performance optimization validation
2. User experience assessment
3. Instruction accuracy verification

---

## Test Execution Log

Use this section to track testing progress:

**Date**: _______________
**Tester**: _______________
**Version**: _______________

### Critical Issues Found:
- [ ] Issue 1: _______________
- [ ] Issue 2: _______________
- [ ] Issue 3: _______________

### Minor Issues Found:
- [ ] Issue 1: _______________
- [ ] Issue 2: _______________
- [ ] Issue 3: _______________

### Instruction Discrepancies:
- [ ] Discrepancy 1: _______________
- [ ] Discrepancy 2: _______________
- [ ] Discrepancy 3: _______________

### Overall Assessment:
- **Functionality**: ___/10
- **Usability**: ___/10
- **Instruction Accuracy**: ___/10
- **Readiness for Release**: ___/10

### Notes:
_________________________________
_________________________________
_________________________________