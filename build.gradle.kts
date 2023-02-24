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

    implementation(fileTree("lib") { include("*.jar") })
    runtimeOnly("org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.7.10")
    runtimeOnly("org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm:1.5.0")
    runtimeOnly("it.unimi.dsi:fastutil:8.5.2")
    runtimeOnly("com.google.guava:guava:31.1-jre")

    testImplementation("org.assertj:assertj-core:latest.release")
    testImplementation("org.junit.jupiter:junit-jupiter-api:latest.release")
    testImplementation("org.junit.jupiter:junit-jupiter-params:latest.release")
    testImplementation("org.openrewrite:rewrite-test")

    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:latest.release")
}
