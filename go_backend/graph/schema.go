package graph

type MathEntityType string

const (
	Axiom      MathEntityType = "Axiom"
	Definition MathEntityType = "Definition"
	Lemma      MathEntityType = "Lemma"
	Theorem    MathEntityType = "Theorem"
	Corollary  MathEntityType = "Corollary"
	Proof      MathEntityType = "Proof"
	Example    MathEntityType = "Example"
	Concept    MathEntityType = "Concept"
)

type MathRelationType string

const (
	UsesAxiom       MathRelationType = "USES_AXIOM"
	UsesDefinition  MathRelationType = "USES_DEFINITION"
	UsesLemma       MathRelationType = "USES_LEMMA"
	Proves          MathRelationType = "PROVES"
	CorollaryOf     MathRelationType = "COROLLARY_OF"
	PrerequisiteFor MathRelationType = "PREREQUISITE_FOR"
	DependsOn       MathRelationType = "DEPENDS_ON"
)

type GraphNode struct {
	ID          string         `json:"id"`
	Name        string         `json:"name"`
	EntityType  MathEntityType `json:"entity_type"`
	Description string         `json:"description"`
}

type GraphEdge struct {
	Source   string           `json:"source"`
	Target   string           `json:"target"`
	Relation MathRelationType `json:"relation"`
}

type MathEntityExtraction struct {
	Nodes []GraphNode `json:"nodes"`
	Edges []GraphEdge `json:"edges"`
}
