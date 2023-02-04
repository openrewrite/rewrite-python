plugins {
    id("org.openrewrite.build.language-library") version "latest.release"
}
group = "org.openrewrite"
description = "Rewrite Python"

dependencies {
    annotationProcessor("org.projectlombok:lombok:latest.release")

    compileOnly("org.openrewrite:rewrite-test")
    compileOnly("org.projectlombok:lombok:latest.release")

    implementation(platform("org.openrewrite.recipe:rewrite-recipe-bom:latest.integration"))
    implementation("org.openrewrite:rewrite-java")

    implementation(files("lib/intellij-python-plugin.jar"))

    testImplementation("org.assertj:assertj-core:latest.release")
    testImplementation("org.junit.jupiter:junit-jupiter-api:latest.release")
    testImplementation("org.junit.jupiter:junit-jupiter-params:latest.release")
    testImplementation("org.openrewrite:rewrite-test")

    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:latest.release")
}
