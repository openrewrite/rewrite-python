plugins {
    id("org.openrewrite.build.recipe-library") version "latest.release"
}

group = "org.openrewrite"
description = "Rewrite Python"

val latest = if (project.hasProperty("releasing")) {
    "latest.release"
} else {
    "latest.integration"
}

dependencies {
    compileOnly("org.openrewrite:rewrite-test")
    compileOnly("org.openrewrite:rewrite-remote-java:latest.integration") {
        exclude(group = "org.openrewrite", module = "rewrite-python")
    }

    implementation(platform("org.openrewrite:rewrite-bom:$latest"))
    implementation("org.openrewrite:rewrite-core")
    implementation("org.openrewrite:rewrite-java")

    testImplementation("org.openrewrite:rewrite-test")
    testImplementation("org.junit-pioneer:junit-pioneer:latest.release")

    testRuntimeOnly("org.openrewrite:rewrite-remote-java:latest.integration") {
        exclude(group = "org.openrewrite", module = "rewrite-python")
    }
}
